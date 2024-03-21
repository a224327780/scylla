from tasks.base import BaseTask


class ValidateMjj(BaseTask):
    validate_url = 'https://share.cjy.me/mjj6/'
    concurrency = 1

    async def process_start_urls(self):
        cond = {'status': 1, 'is_mjj': {'$in': [ 1]}}
        async for item in self.col.find(cond).limit(100):
            scheme = item['proxy_type'].lower()
            proxy = f"{scheme}://{item['_id']}:{item['port']}"

            data = dict(item)
            data['proxy'] = proxy
            data['validate_url'] = self.validate_url
            yield self.request(url=self.validate_url, callback=self.validate, metadata=data, proxy=proxy, timeout=30)

    async def validate(self, response, item):
        is_mjj = 0
        status_msg = 'error'
        if response and response.ok:
            html = await response.text()
            if 'users/userinfo' in html:
                is_mjj = 1
                status_msg = 'ok'

        # await self.col.update_one({'_id': item['_id']}, {'$set': {'is_mjj': is_mjj}})
        self.logger.info(f'validate proxy: {item["proxy"]} -> {status_msg}')
