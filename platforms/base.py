# -*- coding: utf-8 -*-
# Filename: base
# Author: brayton
# Datetime: 2019-Oct-16 4:33 PM

from peewee import Model
from peewee import CharField, IntegerField, DateTimeField, IPField, BooleanField, UUIDField

from setting import DATETIME_FORMAT


class BaseLog(Model):

    def __init__(self, *args, **kwargs):
        super(BaseLog, self).__init__(*args, **kwargs)

    username = CharField(verbose_name='cmdb username', index=True, max_length=20)
    remote_addr = CharField(verbose_name='client net ip', max_length=20)
    city = CharField(verbose_name='client address city')
    status = BooleanField(default=True)
    comment = CharField(max_length=500, null=True)
    datetime = DateTimeField(formats=DATETIME_FORMAT, index=True)
    hmac1 = CharField(verbose_name='row log hmac', null=False)
    hmac2 = CharField(verbose_name='related log hmac', null=False)
    invalid = BooleanField(default=True)

    class Meta:
        table_name = 'base_log'
        sensitive_fields = {'username', 'remote_address', 'city', 'status', 'datetime'}

    @classmethod
    def extra_sensitive_fields(cls):
        return cls._meta.sensitive_fields

    @classmethod
    def sensitive_fields(cls):
        return set(BaseLog._meta.sensitive_fields) | set(cls.extra_sensitive_fields())

