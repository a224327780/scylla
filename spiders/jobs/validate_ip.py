import time

from sanic.log import logger

from utils.common import get_bj_date, get_uptime
from utils.db import DB


class ValidateIpJob:

    @classmethod
    async def validate(cls, response, item):
        end_time = time.perf_counter()
        speed = '{:.2f}'.format(end_time - float(item['begin_time']))
        is_ok = response.status == 200
        status = 1 if is_ok else 2
        data = {
            'status': status,
            'speed': speed,
            'last_time': get_bj_date(),
            'check_count': int(item['check_count']) + 1,
            'fail_count': 0 if is_ok else int(item['fail_count']) + 1,
            'uptime': get_uptime(item['last_time'], item['uptime']) if is_ok else 0
        }
        col = DB.get_col()
        await col.update_one({'_id': item['_id']}, {'$set': data})
        logger.info(f'validate ip:{item["_id"]} -> {response.status}')
