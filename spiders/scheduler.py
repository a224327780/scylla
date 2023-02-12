import asyncio
import time
from datetime import timedelta

from spiders.base.spider import Spider
from spiders.jobs.fetch_ip import FetchIpJob
from spiders.jobs.validate_ip import ValidateIpJob
from utils.common import get_extractors, get_bj_date
from utils.db import DB


class Scheduler(Spider):
    country_ip_lock = asyncio.Lock()

    async def fetch_ip(self):
        async for (name, extractor) in get_extractors():
            urls = await extractor.urls()
            for url in urls:
                # if '89ip' not in url:
                #     continue
                yield self.request(url=url, callback=FetchIpJob.parse_ip, metadata=extractor, timeout=10)

    async def country_ip(self):
        col = DB.get_col()
        api = 'http://ip-api.com/batch'
        while True:
            if self.country_ip_lock.locked():
                await asyncio.sleep(1)
                continue

            self.logger.info('start country ip')
            ip_list = []
            try:
                async for item in col.find({'status': 1, 'country': ''}).limit(50):
                    ip_list.append(item['_id'])
                if len(ip_list):
                    response = await self.fetch(url=api, json=ip_list, method='POST', timeout=15)
                    data = await response.json()
                    col = DB.get_col()
                    for item in data:
                        ip = item['query']
                        country_code = item['countryCode']
                        self.logger.info(f"{ip} -> {country_code}")
                        await col.update_one({'_id': ip}, {'$set': {'country': country_code}})
            except Exception as e:
                self.logger.error(e)
            finally:
                await self.country_ip_lock.acquire()

    async def validate_ip(self):
        col = DB.get_col()
        async for item in col.find().sort([('status', 1, ('last_time', 1))]).limit(200):
            # url = 'http://httpbin.org/ip' if item['is_cn'] else 'http://t66y.com/index.php'
            url = 'http://httpbin.org/ip'
            scheme = item['proxy_type'].lower().replace('https', 'http')
            proxy = f"{scheme}://{item['_id']}:{item['port']}"
            item['begin_time'] = time.perf_counter()
            yield self.request(url=url, callback=ValidateIpJob.validate, metadata=item, proxy=proxy)

    async def clean_fail(self):
        day_1_ago = (get_bj_date() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        selector = {'status': 2, 'last_time': {'$lt': day_1_ago}}
        col = DB.get_col()
        while True:
            async for item in col.find(selector).limit(200):
                self.logger.info(f'delete fail ip: {item["_id"]}')
                await col.delete_one({'_id': item['_id']})
            await asyncio.sleep(3600 * 6)

    async def validate_ip_after(self, task_result):
        if self.country_ip_lock.locked():
            self.country_ip_lock.release()

    async def run(self):
        # 获取ip
        fetch_ip_task = self.start_worker('fetch_ip', 'fetch ip', 3600)
        self.worker.append(asyncio.ensure_future(fetch_ip_task))

        # 验证ip
        validate_ip_task = self.start_worker('validate_ip', 'validate ip', 120, self.validate_ip_after)
        self.worker.append(asyncio.ensure_future(validate_ip_task))

        # 删除一天前验证失败
        self.worker.append(asyncio.ensure_future(self.clean_fail()))

        # 更新ip地区
        self.worker.append(asyncio.ensure_future(self.country_ip()))
