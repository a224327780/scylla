import os

from sanic import Request, Blueprint
from sanic.response import empty

from utils.common import serializer, get_bj_date, get_utc_date, format_date
from utils.db import DB

bp_home = Blueprint('home')


@bp_home.get('/', name='index')
@serializer()
async def index(request: Request):
    config = request.app.config
    return {'dev': config.DEV}


@bp_home.get('/ip2', name='ip')
@serializer()
async def get_ip(request: Request):
    headers = {a: b for a, b in request.headers.items()}
    data = {
        'ip': request.remote_addr,
        'ip2': request.ip,
        'request': request.url,
        'forwarded': request.forwarded,
        'headers': headers,
        'host': request.host,
        'bj_date': get_bj_date(),
        'utc_date': get_utc_date()
    }
    return data


@bp_home.get('/robot.txt', name='robot_file')
async def robot_file(request):
    return empty()


@bp_home.get('/e1')
@serializer()
async def envs(request):
    return dict(os.environ)


@bp_home.get('/proxies')
@serializer()
async def run_os(request: Request):
    col = DB.get_col()
    data = []
    async for item in col.find({'status': 1}).sort('last_time', -1).limit(20):
        proxy = {
            'ip': item['_id'],
            'port': item['port'],
            'type': item['proxy_type'],
            'country': item['country'],
            'last_check': format_date(item['last_time'])
        }
        data.append(proxy)
    return data
