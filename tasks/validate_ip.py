import asyncio
import time

from tasks.base import BaseTask
from utils.common import get_bj_date, get_uptime


class ValidateIpTask(BaseTask):
    concurrency = 20
    cn_validate_url = 'http://connect.rom.miui.com/generate_204'
    no_cn_validate_url = 'http://cp.cloudflare.com'

    async def process_start_urls(self):
        sort = [('status', 1), ('last_time', 1)]
        async for item in self.col.find({'country': {'$ne': ''}}).sort(sort).limit(200):
            data = self.get_start_url_data(item)
            yield self.request(url=data['validate_url'], callback=self.validate, metadata=data,
                               proxy=data['validate_url'], timeout=30)

    def get_start_url_data(self, item):
        validate_url = self.cn_validate_url if item['country'] == 'CN' else self.no_cn_validate_url
        scheme = item['proxy_type'].lower().replace('https', 'http')
        proxy = f"{scheme}://{item['_id']}:{item['port']}"
        data = dict(item)
        data['proxy'] = proxy
        data['validate_url'] = validate_url
        data['begin_time'] = time.perf_counter()
        return data

    async def validate(self, response, item):
        end_time = time.perf_counter()
        begin_time = item.pop('begin_time')
        speed = '{:.2f}'.format(end_time - float(begin_time))
        is_ok = response and response.status in [200, 204]
        status = 1 if is_ok else 2
        status_msg = 'ok' if is_ok else 'error'
        data = {
            'status': status,
            'speed': speed if is_ok else 0,
            'last_time': get_bj_date(),
            'check_count': int(item['check_count']) + 1,
            'fail_count': 0 if is_ok else int(item['fail_count']) + 1,
            'uptime': get_uptime(item['last_time'], item['uptime']) if is_ok else 0
        }
        await self.col.update_one({'_id': item['_id']}, {'$set': data})
        self.logger.info(f'validate proxy: {item["proxy"]} -> {status_msg}')

    async def request(self, url: str, callback=None, metadata=None, **request_config):
        response = None
        try:
            async with self.sem:
                response = await self.fetch(url, **request_config)
                if response and not response.ok:
                    self.logger.debug(f"<Error: {url} {response.status}>")
        except asyncio.TimeoutError:
            self.logger.debug(f"<Error: {url} Timeout>")
        except Exception as e:
            self.logger.debug(f"<Error: {url} {e}>")

        callback_result = None
        try:
            callback_result = await callback(response, metadata)
        except Exception as e:
            self.logger.exception(e)
        return callback_result, response
