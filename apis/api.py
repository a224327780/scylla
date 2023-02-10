from urllib import parse

from sanic import Blueprint, Request
from sanic.exceptions import SanicException

from utils.common import serializer, md5, get_bj_date
from utils.db import DB

bp_api = Blueprint('api', url_prefix='api')


@bp_api.post('/agent.add')
@serializer()
async def agent(request: Request):
    agent_name = request.form.get('agent_name')
    _id = md5(agent_name)
    col = DB.get_col()
    data = await col.find_one({'_id': _id})
    if not data:
        data = {'name': agent_name, '_id': _id, 'create_date': get_bj_date()}
        await col.insert_one(data)
    return f"curl {request.url_for(f'script.install_sh', aid=_id)} | bash"


@bp_api.post('/agent.json', name='agent_json')
@serializer()
async def agent(request: Request):
    message = request.body.decode('utf-8')
    col = DB.get_col()
    data = dict(parse.parse_qsl(message))
    if 'token' not in data:
        raise SanicException('missing a required argument: token')

    aid = data.pop('token')
    data['update_date'] = get_bj_date()
    await col.update_one({'_id': aid}, {'$set': data})
    return message
