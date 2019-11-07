# -*- coding: utf-8 -*-
# Filename: server
# Author: brayton
# Datetime: 2019-Oct-11 6:04 PM

import asyncio
import opentracing
from basictracer import BasicTracer
from sanic import Sanic
from sanic.response import json as sanic_json, text, HTTPResponse

from core import load_config
from core.db import ConnectionPool
from core.loggers import AioReporter
from core.openapi import blueprint as openapi_blueprint
from core.service import ServiceManager, service_watcher
from core.exceptions import Unauthorized
from core.utils import CustomHandler, consume, before_request
from utils.auth import JSONWebTokenAuthentication

config = load_config()
app_name = config.get('SERVICE_NAME', __name__)
consul_enabled = config.get('CONSUL_ENABLED', False)
logging_config = config.get('LOGGING_CONFIG', None)
app = Sanic(app_name, error_handler=CustomHandler(), log_config=logging_config)
app.config = config
app.blueprint(openapi_blueprint)


@app.listener('before_server_start')
async def before_server_start(app, loop):
    queue = asyncio.Queue()
    app.queue = queue
    if consul_enabled:
        app.service_manager = ServiceManager(
            consul_host=app.config['CONSUL_AGENT_HOST'],
            consul_port=app.config['CONSUL_AGENT_PORT'],
            loop=loop,
        )
        loop.create_task(service_watcher(app, loop))
    loop.create_task(consume(queue, app))
    reporter = AioReporter(queue=queue)
    tracer = BasicTracer(recorder=reporter)
    tracer.register_required_propagators()
    opentracing.tracer = tracer
    app.db = await ConnectionPool(loop=loop).init(app.config['DB_CONFIG'])


@app.listener('after_server_start')
async def after_server_start(app, loop):
    if consul_enabled:
        await app.service_manager.register_service(
            app.name, app.config['SERVICE_ID'],
            app.config['SERVICE_HOST'], app.config['SERVICE_PORT']
        )


@app.listener('before_server_stop')
async def before_server_stop(app, loop):
    if consul_enabled:
        await app.service_manager.deregister(app.config['SERVICE_ID'])
        app.service_manager.close()
        del app.service_manager
    app.queue.join()


@app.middleware('request')
async def cros(request):
    config = request.app.config
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': config['ACCESS_CONTROL_ALLOW_ORIGIN'],
            'Access-Control-Allow-Headers': config['ACCESS_CONTROL_ALLOW_HEADERS'],
            'Access-Control-Allow-Methods': config['ACCESS_CONTROL_ALLOW_METHODS']
        }
        return sanic_json({'code': 0}, headers=headers)
    if request.method == 'POST' or request.method == 'PUT':
        request['data'] = request.sanic_json
    span = before_request(request)
    request['span'] = span


@app.middleware('request')
async def authenticate(request):
    author = JSONWebTokenAuthentication()
    try:
        user_auth_tuple = author.authenticate(request)
    except Unauthorized as e:
        raise e


@app.middleware('response')
async def cors_res(request, response):
    config = request.app.config
    span = request['span'] if 'span' in request else None
    if response is None:
        return response
    result = {'code': 0}
    if not isinstance(response, HTTPResponse):
        if isinstance(response, tuple) and len(response) == 2:
            result.update({
                'data': response[0],
                'pagination': response[1]
            })
        else:
            result.update({'data': response})
        response = sanic_json(result)
        if span:
            span.set_tag('http.status_code', "200")
    if span:
        span.set_tag('component', request.app.name)
        span.finish()
    response.headers["Access-Control-Allow-Origin"] = config['ACCESS_CONTROL_ALLOW_ORIGIN']
    response.headers["Access-Control-Allow-Headers"] = config['ACCESS_CONTROL_ALLOW_HEADERS']
    response.headers["Access-Control-Allow-Methods"] = config['ACCESS_CONTROL_ALLOW_METHODS']
    return response
