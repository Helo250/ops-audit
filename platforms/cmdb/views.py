# -*- coding: utf-8 -*-
# Filename: views
# Author: brayton
# Datetime: 2019-Oct-14 11:34 AM

from sanic.blueprints import Blueprint

from core.doc import consumes

cmdb_bp = Blueprint('cmdb')


@cmdb_bp.get('/login', name='get_login_logs')
async def get_login_logs(request):
    async with request.app.db.acquire(request) as cur:
        logs = await cur.fetch("SELECT * FROM login_log")
    return logs


@cmdb_bp.get('/login/<log_id:int>', name='get_login_log')
async def get_login_log(request, log_id):
    async with request.app.db.acquire(request) as cur:
        log = await cur.fetch('SELECT * FROM login_log where id=$1', log_id)
    return log


@cmdb_bp.get('/user/<cmdb_uid:int>/login', name='get_user_login_log')
async def get_user_login_log(request, cmdb_uid):
    async with request.app.db.acquire(request) as cur:
        logs = await cur.fetch('SELECT * FROM login_log where cmdb_uid=$1', cmdb_uid)
    return logs
