import json

from extractors.base import BaseExtractor


class ProxyScrape(BaseExtractor):
    api = 'https://api.proxyscrape.com/v3/free-proxy-list/get'

    async def urls(self) -> [str]:
        return [f'{self.api}?request=displayproxies&proxy_format=protocolipport&format=json&limit=200']

    async def parse(self, document):
        html = document.html()
        data = json.loads(html)
        for item in data['proxies']:
            country = ''
            if 'ip_data' in item:
                country = item['ip_data']['countryCode']
            yield {'ip': item['ip'], 'port': item['port'], 'proxy_type': item['protocol'],
                   'country': country}
