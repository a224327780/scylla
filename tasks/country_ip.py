from tasks.base import BaseTask


class CountryIpTask(BaseTask):
    api = 'http://ip-api.com/batch'

    async def process_start_urls(self):
        ip_list = []
        async for item in self.db.get_country_empty():
            ip_list.append(item['id'])

        if len(ip_list):
            yield self.request(url=self.api, callback=self.update_country, timeout=15, json=ip_list)
        else:
            yield []

    async def update_country(self, response, metadata):
        if response is None:
            return

        data = await response.json()
        self.logger.info(data)
        for item in data:
            ip = item['query']
            country_code = item['countryCode']
            is_cn = 1 if country_code in ['CN', 'HK'] else 0
            self.logger.info(f"{ip} -> {country_code}")
            await self.db.update(ip, {'country': country_code, 'is_cn': is_cn})