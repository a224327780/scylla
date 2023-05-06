import asyncio
import time

from spiders.base.spider import Spider
from spiders.jobs.fetch_ip import FetchIpJob
from spiders.jobs.validate_ip import ValidateIpJob
from utils.common import get_extractors
from utils.db import DB


class Scheduler(Spider):

    async def fetch_ip(self):
        headers = self.headers
        async for (name, extractor) in get_extractors():
            extractor.name = name
            urls = await extractor.urls()
            # if not urls or name != 'geonode':
            #     continue

            self.logger.info(f'fetch ip by: {name}')
            request_config = extractor.request_config
            if request_config:
                headers = self.headers.copy()
                headers.update(request_config)

            for url in urls:
                yield self.request(url=url, callback=FetchIpJob.parse_ip, metadata=extractor, timeout=15,
                                   headers=headers)

    async def country_ip(self):
        col = DB.get_col()
        api = 'http://ip-api.com/batch'

        while True:
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
                        is_cn = 1 if country_code in ['CN', 'HK'] else 0
                        self.logger.info(f"{ip} -> {country_code}")
                        await col.update_one({'_id': ip}, {'$set': {'country': country_code, 'is_cn': is_cn}})
            except Exception as e:
                self.logger.error(e)
            await asyncio.sleep(120)

    async def validate_ip(self):
        db = DB.get_db()
        selector = {'status': {'$gte': 0}}
        resp = db.get_query_result(selector, raw_result=True, limit=200, sort=['last_time', 'status'])
        for doc in resp['docs']:
            # url = 'http://www.gstatic.com/generate_204'
            url = 'https://api.ipify.org/'
            scheme = doc['proxy_type'].lower().replace('https', 'http')
            proxy = f"{scheme}://{doc['_id']}:{doc['port']}"
            doc['begin_time'] = time.perf_counter()
            yield self.request(url=url, callback=ValidateIpJob.validate, metadata=doc, proxy=proxy)

        # async for item in col.find().sort([('status', 1), ('last_time', 1)]).limit(200):
        #     url = 'http://www.gstatic.com/generate_204'
        #     scheme = item['proxy_type'].lower().replace('https', 'http')
        #     proxy = f"{scheme}://{item['_id']}:{item['port']}"
        #     item['begin_time'] = time.perf_counter()
        #     yield self.request(url=url, callback=ValidateIpJob.validate, metadata=item, proxy=proxy)

    async def clean_fail(self):
        db = DB.get_db()
        while True:
            selector = {'status': 2, 'fail_count': {'$gte': 3}}
            resp = db.get_query_result(selector, raw_result=True, limit=200)
            for doc in resp['docs']:
                doc.delete()
                self.logger.info(f'delete fail ip: {doc["_id"]}')
            await asyncio.sleep(600)

        # selector = {'status': 2, 'fail_count': {'$gte': 3}}
        # col = DB.get_col()
        # while True:
        #     async for item in col.find(selector).limit(300):
        #         self.logger.info(f'delete fail ip: {item["_id"]}')
        #         await col.delete_one({'_id': item['_id']})
        #     await asyncio.sleep(600)

    async def run(self):
        # 获取ip
        # fetch_ip_task = self.start_worker('fetch_ip', 'fetch ip', 3600)
        # self.worker.append(asyncio.ensure_future(fetch_ip_task))

        # 验证ip
        validate_ip_task = self.start_worker('validate_ip', 'validate ip', 150)
        self.worker.append(asyncio.ensure_future(validate_ip_task))

        # # 删除一天前验证失败
        # self.worker.append(asyncio.ensure_future(self.clean_fail()))

        # # 更新ip地区
        # self.worker.append(asyncio.ensure_future(self.country_ip()))
