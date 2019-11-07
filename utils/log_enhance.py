# -*- coding: utf-8 -*-
# Filename: log_enhance
# Author: brayton
# Datetime: 2019-Oct-16 4:24 PM


import hmac
import psycopg2
from collections import namedtuple
from functools import reduce
from base64 import b64encode, b64decode

from setting import SECRET_KEY, DB_CONFIG, PROJECT_ROOT
from platforms import cmdb



# cur.execute()
import os

log_model_map = {
    'LoginLog': cmdb.models.LoginLog,
    'FTPLog': cmdb.models.FTPLog
}


def insert_log(log):
    data, table, fields = prepare_log(log)
    sql_1 = f"""
    INSERT INTO 
    {table} ({','.join(fields)}, hmac1, hmac2) 
    VALUES   
    (
        {'%s,' * len(fields)}
        '{data['hmac1']}', 
        ENCODE(HMAC(
            '{SECRET_KEY}', 
            CONCAT('{data['hmac1']}', '.', (SELECT 'hmac2' FROM {table} ORDER BY id desc LIMIT 1 FOR UPDATE)),
            'md5'
            ), 'hex')
    );
    """
    sql_2 = [data[field] for field in fields]
    return sql_1, sql_2


def prepare_log(log: namedtuple):
    try:
        LogModel = log_model_map[log.__class__.__name__]
    except KeyError:
        raise
    sensitive_fields = sorted(LogModel.sensitive_fields())
    log_dic_python = log._asdict()
    log_dic_python['hmac1'] = encrypt_log(log_dic_python, sensitive_fields)
    table = LogModel._meta.table_name

    log_dic_db = {
        field.column_name: field.db_value(value)
        for field, value in LogModel._normalize_data(None, log_dic_python).items()
    }
    fields = log._fields
    return log_dic_db, table, fields


def encrypt_log(log, sensitive_fields):
    sensitive_data = '&'.join(map(lambda k: str(log.get(k, '')), sensitive_fields))
    hmac_algo = b64encode('&'.join(sensitive_fields).encode()).decode()
    hmac_value = hmac.HMAC(SECRET_KEY.encode(), sensitive_data.encode()).hexdigest()
    return f'{hmac_value}.{hmac_algo}'


def validate_log(log: dict):
    value, algo = log.get('hmac1').split('.')
    sensitive_data = '&'.join(map(lambda k: str(log.get(k, '')), b64decode(algo.encode()).decode().split('&')))
    return value == hmac.new(SECRET_KEY.encode(), sensitive_data.encode()).hexdigest()


def test_insert():
    from log_stream.logs import LoginLog
    login = LoginLog(
        cmdb_uid=1,
        username='shen',
        ip='192.168.0.1',
        status=True,
        datetime='2019-12-12 12:00:00',
        media='web',
        agent='test-agent',
        net='wlan'
    )
    sql_1, sql_2 = insert_log(login)
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    print(cur.execute(sql_1, list(sql_2)))
    # cur.execute('select count(*) from login_log')
    # row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return ''

# a = hello('li')
#
#
if __name__ == '__main__':
    # load_all_models()
    test_insert()

