# -*- coding: utf-8 -*-
# Filename: setting
# Author: brayton
# Datetime: 2019-Oct-12 10:51 AM

import os
import yaml
import dill
import datetime

PROJECT_ROOT = os.path.dirname(__file__)

SERVICE_NAME = 'cmdb-audit-service'
SERVICE_ID = 'cmdb-audit-service01'

SERVICE_HOST = os.environ.get('SERVER_HOST', 'localhost')
SERVICE_PORT = os.environ.get('SERVER_PORT', 8050)

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
SECRET_KEY = 'XXXXXXXXXXXXXXXX'

DB_CONFIG = {
    'host':  os.environ.get('POSTGRES_SERVICE_HOST', 'localhost'),
    'user': os.environ.get('POSTGRES_SERVICE_USER', 'brayton'),
    'password': os.environ.get('POSTGRES_SERVICE_PASSWORD', 'wang1234'),
    'port': os.environ.get('POSTGRES_SERVICE_PORT', 5432),
    'database': os.environ.get('POSTGRES_SERVICE_DB_NAME', 'cmdb_audit')
}

SWAGGER = {
    'version': '1.0.0',
    'title': 'CMDB AUDIT API',
    'description': 'CMDB AUDIT API',
    'terms_of_service': 'Use with caution!',
    'termsOfService': ['application/json'],
    'contact_email': 'shenwei@huored.cn'
}

JWT_AUTH = {
    'SECRET_KEY': 'y_3$q&g8h=(v@w@2dyu33z%xa2^e%)^h314z47_fvw8ii)6coo',
    'GET_USER_SECRET_KEY': None,
    'PUBLIC_KEY': None,
    'PRIVATE_KEY': None,
    'ALGORITHM': 'HS256',
    'VERIFY': True,
    'VERIFY_EXPIRATION': True,
    'LEEWAY': 0,
    'EXPIRATION_DELTA': datetime.timedelta(seconds=30000),
    'AUDIENCE': None,
    'ISSUER': None,

    'ALLOW_REFRESH': True,
    'REFRESH_EXPIRATION_DELTA': datetime.timedelta(days=7),

    'AUTH_HEADER_PREFIX': 'JWT',
    'AUTH_COOKIE': None,
}

with open(os.path.join(os.path.dirname(__file__), 'logging.yml'), 'r') as logging:
    LOGGING_CONFIG = yaml.safe_load(logging)

ZIPKIN_SERVER = os.environ.get('ZIPKIN_SERVER', None)
ACCESS_CONTROL_ALLOW_ORIGIN = os.environ.get("ACCESS_CONTROL_ALLOW_ORIGIN", "")
ACCESS_CONTROL_ALLOW_HEADERS = os.environ.get("ACCESS_CONTROL_ALLOW_HEADERS", "")
ACCESS_CONTROL_ALLOW_METHODS = os.environ.get("ACCESS_CONTROL_ALLOW_METHODS", "")

CONSUL_ENABLED = False
CONSUL_AGENT_HOST = os.environ.get('CONSUL_AGENT_HOST', '127.0.0.1')
CONSUL_AGENT_PORT = os.environ.get('CONSUL_AGENT_PORT', 8500)
SERVICE_WATCH_INTERVAL = 60

KAFKA_SERIALIZER = dill.dumps
KAFKA_DESERIALIZER = dill.loads
