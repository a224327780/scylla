from tasks.base import BaseTask


class CountryIpTask(BaseTask):

    api = 'http://ip-api.com/batch'

    async def process_start_urls(self):
        ip_list = []
        async for item in self.col.find({'country': ''}).limit(30):
            ip_list.append(item['_id'])

        if len(ip_list):
            yield self.request(url=self.api, callback=self.update_country, timeout=15, json=ip_list)
        else:
            yield []

    async def update_country(self, response, metadata):
        if response is None:
            return

        data = await response.json()
        for item in data:
            ip = item['query']
            country_code = item['countryCode']
            self.logger.info(f"{ip} -> {country_code}")
            await self.col.update_one({'_id': ip}, {'$set': {'country': country_code}})
