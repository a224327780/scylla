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
    db: DB = request.app.ctx.db
    data = []
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))
    offset = (page - 1) * limit
    where = "status = 1 and country <> ''"
    async for item in db.query(where, order_by='last_time desc', limit=limit, offset=offset):
        proxy = {
            'ip': item['id'],
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
    db: DB = request.app.ctx.db
    data = {'items': [], 'total': 0}
    async for item in db.query('status = 1', group_by='country', fields='id, country, count(country) total'):
        data['total'] += int(item['total'])
        data['items'].append({'country': item['country'], 'total': item['total']})
    return data
