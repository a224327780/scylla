import os
from traceback import format_exc

from sanic import Sanic
from sanic import json as json_response
from sanic.log import logger

from apis.home import bp_home
from spiders.scheduler import Scheduler
from utils import config
from utils.common import fail, success
from utils.db import DB
from utils.log import DEFAULT_LOGGING

app = Sanic('scylla', log_config=DEFAULT_LOGGING)
app.config.update_config(config)

app.static('/favicon.ico', 'static/favicon.png')
app.blueprint(bp_home)


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
    logger.exception(exception)
    data = fail(message, format_exc(), code)
    if code == 777:
        code = 200
        data = success()
    return json_response(data, code)


@app.listener('before_server_start')
async def setup_db(_app: Sanic, loop) -> None:
    DB.init_db(loop, 'db0', 'scylla')


@app.listener('after_server_start')
async def setup_db(_app: Sanic, loop) -> None:
    _app.ctx.scheduler = scheduler = Scheduler()
    await app.add_task(scheduler.run())


@app.listener('before_server_stop')
async def setup_db(_app: Sanic, loop) -> None:
    DB.close_db()
    await _app.ctx.scheduler.cancel()


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)), access_log=config.DEV, dev=False, fast=config.PROD)
