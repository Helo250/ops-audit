# -*- coding: utf-8 -*-
# Filename: service
# Author: brayton
# Datetime: 2019-Oct-12 10:32 AM

import logging
import consul
import consul.aio
import socket
import asyncio
import aiohttp

from collections import defaultdict

logger = logging.getLogger('sanic.root')
consul_state = True


class ServiceInfo(object):
    """
    service info object class
    """
    def __init__(self, node, address, datacenter,
                 service_name, service_id, service_address, service_port,
                 service_tags, service_weights, service_proxy,
                 create_index=None, modify_index=None
                 ):
        self.service_name = service_name
        self.service_id = service_id
        self.service_address = service_address
        self.service_port = service_port
        self.service_tags = service_tags
        self.service_weights = service_weights,
        self.service_proxy = service_proxy,
        self.node = node
        self.address = address
        self.datacenter = datacenter
        self.create_index = create_index
        self.modify_index = modify_index

    def __eq__(self, value):
        return self.service_id == value.service_id

    def __ne__(self, value):
        return (not self.__eq__(value))

    def __hash__(self):
        return hash(self.service_id or self.service_address or self.service_name)


class ServiceManager(object):
    def __init__(self, consul_host, consul_port, loop=None, **kwargs):
        global consul_state
        consul_state = self.check_consul_state(consul_host, consul_port)
        if not consul_state or not consul_host or not consul_port:
            raise ValueError('service manager not support')
        self.consul = consul.aio.Consul(host=consul_host, port=consul_port, loop=loop, **kwargs)

    def check_consul_state(self, host, port):
        return socket.socket(socket.AF_INET, socket.SOCK_DGRAM).connect((host, port)) and True

    def get_host_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        print('>>>>>>>>>>', s.getsockname())
        ip = s.getsockname()[0]
        s.close()
        return ip

    def close(self):
        self.consul.close()

    async def register_service(self, service_name, service_id, service_host=None, service_port=None):
        service_host = service_host or self.get_host_ip()
        service = self.consul.agent.service
        check = consul.Check.tcp(service_host, service_port, '60s')
        res = await service.register(service_name, service_id, address=service_host, port=service_port, check=check)
        logger.info(f'register service {service_name}({service_id}[{service_host}:{service_port}]) {"successfully" if res else "failed"}')

    async def deregister(self, service_id):
        service = self.consul.agent.service
        await service.deregister(service_id)
        logger.info('deregister service: {}'.format(service_id))

    async def discovery_service(self, service_name):
        catalog = self.consul.catalog
        _, nodes = await catalog.service(service_name)
        services = []
        for node in nodes:
            services.append(ServiceInfo(
                node=node['Node'],
                address=node['Address'],
                datacenter=node['Datacenter'],
                service_name=node['ServiceName'],
                service_id=node['ServiceID'],
                service_address=node['ServiceAddress'],
                service_port=node['ServicePort'],
                service_tags=node['ServiceTags'],
                service_weights=node['ServiceWeights'],
                service_proxy=node['ServiceProxy']
            ))
        return services

    async def discovery_services(self):
        catalog = self.consul.catalog
        _, services = await catalog.services()
        return services

    async def check_service(self, service_name):
        health = self.consul.health
        _, checks = await health.checks(service_name)
        res = {}
        for check in checks:
            res[check['ServiceID']] = check
        return res


async def service_watcher(app, loop):
    """
    async function to find service
    :param app: sanic instance
    :param loop: event loop
    :return:
    """
    service = getattr(app, 'service_manager', None)
    if not service:
        service = ServiceManager(
            loop=loop,
            consul_host=app.config['CONSUL_AGENT_HOST'],
            consul_port=app.config['CONSUL_AGENT_PORT']
        )
    logger.info('service watcher...')
    app.services = defaultdict(set)
    interval = app.config['SERVICE_WATCH_INTERVAL']
    while True:
        for name in await service.discovery_services():
            if 'consul' == name:
                continue
            checks = await service.check_service(name)
            for service in await service.discovery_service(name):
                status = checks[service.service_id]['Status']
                if status == 'passing':
                    app.services[name].add(service)
                elif status == 'passing':
                    app.services[name].discard(service)
        await asyncio.sleep(interval)
