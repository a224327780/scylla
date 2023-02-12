import os

from sanic import Request, Blueprint
from sanic.response import empty

from utils.common import serializer, get_bj_date, get_utc_date, format_date, format_uptime
from utils.db import DB

bp_api = Blueprint('api', url_prefix='api')
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


@bp_api.get('/proxies')
@serializer()
async def proxies(request: Request):
    col = DB.get_col()
    data = []
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))
    offset = (page - 1) * limit
    async for item in col.find({'status': 1, 'country': {'$ne': ''}}).sort('last_time', -1).limit(limit).skip(offset):
        proxy = {
            'ip': item['_id'],
            'port': item['port'],
            'type': item['proxy_type'],
            'country': item['country'],
            'uptime': format_uptime(item['uptime']),
            'last_check': format_date(item['last_time'])
        }
        data.append(proxy)
    return data


@bp_api.get('/country')
@serializer()
async def country(request: Request):
    col = DB.get_col()
    data = {'items': [], 'total': 0}
    pip = [
        {
            '$match': {'status': 1}
        },
        {
            '$group': {"_id": "$country", "total": {"$sum": 1}}
        }
    ]
    async for item in col.aggregate(pipeline=pip):
        data['total'] += int(item['total'])
        data['items'].append({'country': item['_id'], 'total': item['total']})
    return data
