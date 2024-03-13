import os
from traceback import format_exc

from aioredis import from_url
from sanic import Sanic
from sanic import json as json_response
from sanic.log import logger

from apis.api import bp_api, bp_home
from tasks.scheduler import Scheduler
from utils import config
from utils.common import fail, success
from utils.db import DB
from utils.log import DEFAULT_LOGGING

app = Sanic('scylla', log_config=DEFAULT_LOGGING)
app.config.update_config(config)


app.static('/favicon.ico', 'static/favicon.png')
app.blueprint(bp_home)
app.blueprint(bp_api)


@app.middleware('response')
def add_cors_headers(request, response):
    headers = {
        "Access-Control-Allow-Methods": "PUT, GET, POST, DELETE, OPTIONS",
        "Access-Control-Allow-Origin": "*",
        'Access-Control-Request-Headers': '*',
        "Access-Control-Allow-Credentials": "true",
        'X-Request-ID': request.id
    }
    response.headers.update(headers)


@app.exception(Exception)
async def catch_anything(request, exception):
    message = exception.message if hasattr(exception, 'message') and exception.message else repr(exception)
    code = 500
    if hasattr(exception, 'status_code'):
        code = exception.status_code
    elif hasattr(exception, 'status'):
        code = exception.status

    logger.error(exception) if code == 404 else logger.exception(exception)
    data = fail(message, format_exc(), code)
    if code == 777:
        code = 200
        data = success()
    return json_response(data, code)


@app.listener('before_server_start')
async def setup_db(_app: Sanic, loop) -> None:
    from aiohttp import ClientSession
    from aiosocksy.connector import ProxyConnector, ProxyClientRequest
    _app.ctx.request_session = ClientSession(connector=ProxyConnector(), request_class=ProxyClientRequest, loop=loop)
    _app.ctx.redis = await from_url(config.REDIS_URI, decode_responses=True)
    DB.init_db(loop, 'db1', 'scylla')


@app.listener('after_server_start')
async def setup_scheduler(_app: Sanic, loop) -> None:
    await Scheduler.run(_app)


@app.listener('before_server_stop')
async def close_db(_app: Sanic, loop) -> None:
    await Scheduler.shutdown()
    await _app.ctx.redis.close()
    DB.close_db()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)), access_log=config.DEV, dev=False, fast=False)
