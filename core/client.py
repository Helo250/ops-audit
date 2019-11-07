# -*- coding: utf-8 -*-
# Filename: client
# Author: brayton
# Datetime: 2019-Oct-12 10:33 AM

import random
import logging
import opentracing
from aiohttp import ClientSession, hdrs

logger = logging.getLogger('sanic.root')


class Client:
    def __init__(self, app, service, **kwargs):
        if not app.config['CONSUL_ENABLED']:
            raise ValueError('Current app can\'t use `Client`, enabled consul support firstly!')
        self._client = ClientSession(loop=app.loop, **kwargs)
        self._app = app
        self.services = app.services[service]

    def handler_url(self, api):
        s = random.choice(list(self.services))
        return f'http://{s.service_address}:{s.service_port}/{api}'

    def request(self, method, api, **kwargs):
        url = self.handler_url(api)
        self._client.request(method, url, **kwargs)

    def cli(self, req):
        operation = f''
        span = opentracing.tracer.start_span(operation_name='get', child_of=req['span'])
        return ClientSessionConn(self, url=self._url, span=span)

    async def close(self):
        await self._client.close()


class ClientSessionConn:
    _client = None

    def __init__(self, client, url=None, span=None, **kwargs):
        self._client = client
        self._url = url
        self._span = span

    def handler_url(self, url):
        if url.startswith("http"):
            return url
        if self._url:
            return "{}/{}".format(self._url, url)
        return url

    def before(self, method, url):
        self._span.log_kv({'event': 'client'})
        self._span.set_tag('http.url', self._url)
        self._span.set_tag('http.path', url)
        self._span.set_tag('http.method', method)
        http_header_carrier = {}
        opentracing.tracer.inject(
            self._span.context,
            format=opentracing.Format.HTTP_HEADERS,
            carrier=http_header_carrier)
        return http_header_carrier

    def request(self, method, url, **kwargs):
        headers = self.before(method, url)
        res = self._client.request(method, self.handler_url(url),
                                   headers=headers, **kwargs)
        self._span.set_tag('component', 'http-client')
        self._span.finish()
        return res

    def get(self, url, allow_redirects=True, **kwargs):
        return self.request(hdrs.METH_GET, url, allow_redirects=True,
                            **kwargs)

    def post(self, url, data=None, **kwargs):
        return self.request(hdrs.METH_POST, url, data=data, **kwargs)

    def put(self, url, data=None, **kwargs):
        return self.request(hdrs.METH_PUT, url, data=data, **kwargs)

    def delete(self, url, **kwargs):
        return self.request(hdrs.METH_DELETE, url, **kwargs)

    def head(self, url, allow_redirects=False, **kwargs):
        return self.request(hdrs.METH_HEAD, url, allow_redirects=allow_redirects, **kwargs)

    def options(self, url, allow_redirects=True, **kwargs):
        return self.request(hdrs.METH_OPTIONS, url, allow_redirects=allow_redirects, **kwargs)

    async def close(self):
        await self._client.close()
