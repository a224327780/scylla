from tasks.base import BaseTask


class CountryIpTask(BaseTask):

    api = 'http://ip-api.com/batch'

    async def process_start_urls(self):
        ip_data = []
        for i in range(11):
            ip_list = []
            offset = i * 30
            async for item in self.col.find({'country': ''}).limit(30).skip(offset):
                ip_list.append(item['_id'])
            ip_data.append(ip_list)

        if len(ip_data):
            for ip_item in ip_data:
                yield self.request(url=self.api, callback=self.update_country, json=ip_item)
        else:
            yield []

    async def update_country(self, response, metadata):
        if response is None:
            return

        data = await response.json()
        for item in data:
            ip = item['query']
            if 'countryCode' in item:
                country_code = item['countryCode']
                self.logger.info(f"{ip} -> {country_code}")
                await self.col.update_one({'_id': ip}, {'$set': {'country': country_code}})
            else:
                self.logger.error(item)
