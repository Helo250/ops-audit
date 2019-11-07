# -*- coding: utf-8 -*-
# Filename: config
# Author: brayton
# Datetime: 2019-Oct-12 10:33 AM

import os
import consul
import consul.aio

DEFAULT_CONFIG = {
    ''
}

class Config:

    def __init__(self, loop, host='127.0.0.1', port=8500):
        self.consul = consul.aio.Consul(host=host)
