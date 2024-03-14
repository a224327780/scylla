import asyncio
import time

from tasks.validate_ip import ValidateIpTask


class CleanFailTask(ValidateIpTask):

    async def process_start_urls(self):
        cond = {'status': 2, 'country': {'$ne': ''}, 'fail_count': {'$lt': 3}}
        async for item in self.col.find(cond).sort('last_time', 1).limit(300):
            validate_url = self.cn_validate_url if item['country'] == 'CN' else self.no_cn_validate_url
            scheme = item['proxy_type'].lower().replace('https', 'http')
            proxy = f"{scheme}://{item['_id']}:{item['port']}"
            data = dict(item)
            data['proxy'] = proxy
            data['validate_url'] = validate_url
            data['begin_time'] = time.perf_counter()
            yield self.request(url=validate_url, callback=self.validate, metadata=data, proxy=proxy, timeout=30)

    async def after_start_worker(self):
        async for item in self.col.find({'status': 2, 'fail_count': {'$gte': 3}}).limit(200):
            await self.col.delete_one({'_id': item['_id']})
            self.logger.info(f'delete fail ip: {item["id"]}')
