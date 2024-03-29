# -*- coding: utf-8 -*-
# Filename: __init__.py
# Author: brayton
# Datetime: 2019-Oct-11 5:58 PM

import os
from sanic.config import Config


def load_config():
    conf = Config()
    module = os.environ.get('SANIC_SETTINGS_MODULE', 'settings')
    if module:
        path = '%s.py' % module.replace('.', '/')
        conf.from_pyfile(path)
    return conf
