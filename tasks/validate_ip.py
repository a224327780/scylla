import asyncio
import time

from tasks.base import BaseTask
from utils.common import get_bj_date, get_uptime


class ValidateIpTask(BaseTask):
    concurrency = 20

    async def process_start_urls(self):
        sort = [('last_time', 1), ('status', 1)]
        cond = {'fail_count': {'$lt': 2}}
        async for item in self.col.find(cond).sort(sort).limit(300):
            scheme = item['proxy_type'].lower()
            proxy = f"{scheme}://{item['_id']}:{item['port']}"
            # validate_url = 'https://cp.cloudflare.com'
            validate_url = 'https://www.apple.com/library/test/success.html'

            if scheme != 'https':
                validate_url = validate_url.replace('https', 'http')

            data = dict(item)
            data['proxy'] = proxy
            data['validate_url'] = validate_url
            data['begin_time'] = time.perf_counter()

            yield self.request(url=validate_url, callback=self.validate, metadata=data, proxy=proxy, timeout=20)

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
