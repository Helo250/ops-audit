# -*- coding: utf-8 -*-
# Filename: logs
# Author: brayton
# Datetime: 2019-Oct-14 4:37 PM
from collections import namedtuple

base_fields = {'username', 'remote_addr', 'city', 'status', 'datetime', 'comment'}

LoginLog = namedtuple(
    typename='LoginLog',
    field_names=(
        # base fields
        *base_fields,
        # custom
        'media',
        'user_agent'
    )
)

FTPLog = namedtuple(
    typename='FTPLog',
    field_names=(
        # base fields
        *base_fields,
        # custom
        'asset_id',
        'asset_name',
        'system_user',
        'operation',
        'file',
    )
)
