# -*- coding: utf-8 -*-
# Filename: main
# Author: brayton
# Datetime: 2019-Oct-12 10:37 AM

import os
import sys

os.environ['SANIC_SETTINGS_MODULE'] = os.path.dirname(__file__) + '.setting'

import logging
from core.server import app
from log_stream.consume import WorkShop
from log_stream.spec import Task
from platforms.cmdb.views import cmdb_bp

logger = logging.getLogger('sanic.root')

app.register_blueprint(cmdb_bp, url_prefix='/api/logs/cmdb')

bootstrap_servers = 'localhost:9092'


@app.listener('after_server_start')
async def after_server_start(app, loop):
    tasks = {
        Task(cls='login_log', topic='login-log'),
        # Task(cls='ftp_log', topic='ftp-log'),
    }
    app.workshop = WorkShop(tasks, bootstrap_servers, app)
    logger.info('log stream is start!')
    await app.workshop.start()


@app.listener('before_server_stop')
async def before_server_stop(app, loop):
    if app.workshop:
        logger.info('log stream is stop!')
        app.workshop.stop()


@app.route('/')
async def index(request):
    return 'test hello!'


if __name__ == '__main__':
    try:
        app.run(host=app.config['SERVICE_HOST'], port=app.config['SERVICE_PORT'], debug=True)
    except KeyboardInterrupt:
        app.stop()
    finally:
        sys.exit(1)
