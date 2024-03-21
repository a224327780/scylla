import asyncio
import logging

import requests
import urllib3

from utils.db import DB

urllib3.disable_warnings()


class ValidateMjj:

    def __init__(self):
        self.http = requests.session()
        self.headers = {
            'User-Agent': 'ozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36'}
        self.logger = logging.getLogger('sanic.root')
        self.validate_url = 'https://share.cjy.me/mjj6/'
        self.col = None

    @classmethod
    async def run(cls, wait_for=3600):
        ins = cls()
        ins.col = DB.get_col()
        while True:
            try:
                cond = {'status': 1, 'is_mjj': {'$in': [1]}}
                proxy_data = []
                async for item in ins.col.find(cond).limit(100):
                    proxy_data.append(item)
                await asyncio.to_thread(ins.worker, proxy_data=proxy_data)
            except Exception as e:
                ins.logger.error(e)
            finally:
                ins.logger.info(f'Wait {wait_for} seconds.')
                await asyncio.sleep(wait_for)

    def worker(self, proxy_data):
        self.http.headers = self.headers
        self.logger.info(len(proxy_data))
        for item in proxy_data:
            scheme = item['proxy_type'].lower()
            proxy = f"{scheme}://{item['_id']}:{item['port']}"
            proxies = {'http': proxy, 'https': proxy}
            try:
                response = self.http.get(self.validate_url, proxies=proxies, timeout=20, verify=False)
                status_msg = 'error'
                if response and response.ok:
                    html = response.text
                    if 'users/userinfo' in html:
                        is_mjj = 1
                        status_msg = 'ok'

                self.logger.info(f'validate proxy: {proxy} -> {status_msg}')
            except Exception as e:
                self.logger.debug(f'{proxy} -> {e}')

    # async def process_start_urls(self):
    #     cond = {'status': 1, 'is_mjj': {'$in': [1]}}
    #     async for item in self.col.find(cond).limit(100):
    #         scheme = item['proxy_type'].lower()
    #         proxy = f"{scheme}://{item['_id']}:{item['port']}"
    #
    #         data = dict(item)
    #         data['proxy'] = proxy
    #         data['validate_url'] = self.validate_url
    #         yield self.request(url=self.validate_url, callback=self.validate, metadata=data, proxy=proxy, timeout=20)
    #
    # async def validate(self, response, item):
    #     is_mjj = 0
    #     status_msg = 'error'
    #     if response and response.ok:
    #         html = await response.text()
    #         if 'users/userinfo' in html:
    #             is_mjj = 1
    #             status_msg = 'ok'
    #
    #     # await self.col.update_one({'_id': item['_id']}, {'$set': {'is_mjj': is_mjj}})
    #     self.logger.info(f'validate proxy: {item["proxy"]} -> {status_msg}')
