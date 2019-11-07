# -*- coding: utf-8 -*-
# Filename: models
# Author: brayton
# Datetime: 2019-Oct-14 11:33 AM

from peewee import CharField, IntegerField, DateTimeField, IPField, BooleanField, UUIDField, TimestampField
from enum import Enum

from core.utils import list_enum_choices
from platforms.base import BaseLog


class LoginMedia(Enum):
    web = '网页'
    console = '终端'


class LoginLog(BaseLog):
    """
    CMDB login log
    """
    media = CharField(verbose_name='login media', choices=list_enum_choices(LoginMedia), max_length=12, null=True)
    user_agent = CharField(verbose_name='login agent info', null=True)

    class Meta:
        table_name = 'login_log'
        sensitive_fields = ('media', 'user_agent')


class FTPLog(BaseLog):
    """
    FTP operation login
    """
    asset_id = IntegerField(verbose_name='asset id')
    asset_name = CharField(null=True)
    system_user = CharField()
    operation = CharField()
    file = CharField()

    class Meta:
        table_name = 'ftp_log'
        sensitive_fields = ('asset_id', 'system_user', 'operation', 'file')


if __name__ == '__main__':
    # LoginMedia.choices()
    # print(list_enum_choices(LoginMedia))
    print(BaseLog.sensitive_fields())
    print(LoginLog.sensitive_fields())
