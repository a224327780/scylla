import base64
import hashlib
import inspect
import math
from functools import reduce
from datetime import timezone, timedelta, datetime
from functools import wraps
from importlib import import_module
from inspect import isawaitable
from pathlib import Path

from sanic import HTTPResponse, Request, response
from sanic.response import ResponseStream

from extractors.base import BaseExtractor


def get_bj_date(add_seconds=None, fmt='%Y-%m-%d %H:%M:%S'):
    sh_tz = timezone(
        timedelta(hours=8),
        name='Asia/Shanghai',
    )
    utc_dt = datetime.utcnow().replace(tzinfo=timezone.utc)
    bj_now = utc_dt.astimezone(sh_tz)
    if add_seconds:
        bj_now += timedelta(seconds=add_seconds)
    return bj_now.strftime(fmt)


def get_utc_date():
    utc_dt = datetime.utcnow().replace(tzinfo=timezone.utc)
    return utc_dt.strftime('%Y-%m-%d %H:%M:%S')


def md5(string: str):
    m = hashlib.md5()
    m.update(string.encode('utf-8'))
    _md5 = m.hexdigest()
    return _md5[8:-8].upper()


def diff_date_seconds(last_date):
    a = datetime.strptime(str(last_date), '%Y-%m-%d %H:%M:%S')
    b = datetime.strptime(get_bj_date(), '%Y-%m-%d %H:%M:%S')
    return (b - a).seconds


def get_uptime(last_date, uptime=0):
    return diff_date_seconds(last_date) + uptime


def format_date(last_date):
    s = diff_date_seconds(last_date)
    if s <= 0:
        s = 1
    date_name = ['seconds ago', 'minutes ago', 'hours ago']
    i = int(math.floor(math.log(s, 60)))
    if i > len(date_name):
        return last_date

    p = math.pow(60, i)
    return f'{int(s / p)} {date_name[i]}'


def format_uptime(uptime):
    s = int(uptime) / 3600
    if s < 1:
        return f'{int(s * 60)}分钟'
    if s < 24:
        return f'{int(s)}小时'
    return f'{int(s / 24)}天'


def success(data=None, message=''):
    if not data:
        data = []
    return {'code': 0, 'msg': message, 'data': data}


def fail(message='', data=None, code=1):
    if not data:
        data = []
    return {'code': code, 'msg': message, 'data': data}


def serializer():
    def decorator(f):
        @wraps(f)
        async def decorated_function(*args, **kwargs):
            retval = f(*args, **kwargs)
            if isawaitable(retval):
                retval = await retval
            if type(retval) in [HTTPResponse, ResponseStream]:
                return retval
            if type(retval) != dict or not retval.get('code'):
                retval = success(retval)
            if isinstance(args[0], Request):
                _request: Request = args[0]
                # retval['request-id'] = _request.headers
            return response.json(retval)

        return decorated_function

    return decorator


async def get_extractors():
    module_path = 'extractors'
    p = Path(__file__).parent.parent / module_path
    for path in p.glob('**/*.py'):
        module_name = module_path if module_path == path.parent.name else f'{module_path}.{path.parent.name}'
        m = import_module(f'{module_name}.{path.stem}')
        for name, extractor in inspect.getmembers(m):
            if inspect.isclass(extractor) and issubclass(extractor, BaseExtractor) and name != 'BaseExtractor':
                yield name.lower(), extractor()


def get_item_proxy(data):
    if 'country' not in data:
        data['country'] = ''
    if data['country']:
        data['country'] = data['country'].upper()
    data['uptime'] = 0
    data['speed'] = 0
    data['status'] = 0
    data['check_count'] = 0
    data['last_time'] = get_bj_date(-3600 * 12)
    data['fail_count'] = 0
    data['is_mjj'] = -1
    data['proxy_type'] = data['proxy_type'].strip().upper()
    data['port'] = int(str(data['port']).strip())
    return data


def ip_into_int(ip):
    return reduce(lambda x, y: (x << 8) + y, map(int, ip.split('.')))


# 方法1：掩码对比
def is_internal_ip(ip_str):
    ip_int = ip_into_int(ip_str)
    net_a = ip_into_int('10.255.255.255') >> 24
    net_b = ip_into_int('172.31.255.255') >> 20
    net_c = ip_into_int('192.168.255.255') >> 16
    isp = ip_into_int('100.127.255.255') >> 22
    dhcp = ip_into_int('169.254.255.255') >> 16
    return ip_int >> 24 == net_a or ip_int >> 20 == net_b or ip_int >> 16 == net_c or ip_int >> 22 == isp or ip_int >> 16 == dhcp


def b64(data: str) -> str:
    try:
        data = data.encode('ascii')
        rem = len(data) % 4
        if rem > 0:
            data += b"=" * (4 - rem)
        return base64.urlsafe_b64decode(data).decode('utf-8')
    except ValueError:
        return ''
