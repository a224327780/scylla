import hashlib
import inspect
import math
from datetime import timezone, timedelta, datetime
from functools import wraps
from importlib import import_module
from inspect import isawaitable
from pathlib import Path

from sanic import HTTPResponse, Request, response
from sanic.response import ResponseStream

from tasks.extractors.base import BaseExtractor


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
    a = datetime.strptime(last_date, '%Y-%m-%d %H:%M:%S')
    b = datetime.strptime(get_bj_date(), '%Y-%m-%d %H:%M:%S')
    return (b - a).seconds


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
    module_path = 'tasks'
    p = Path(__file__).parent.parent / 'tasks' / 'extractors'
    for path in p.glob('**/*.py'):
        module_name = module_path if module_path == path.parent.name else f'{module_path}.{path.parent.name}'
        m = import_module(f'{module_name}.{path.stem}')
        for name, extractor in inspect.getmembers(m):
            if inspect.isclass(extractor) and issubclass(extractor, BaseExtractor) and name != 'BaseExtractor':
                yield name.lower(), extractor()
