import json

from extractors.base import BaseExtractor


class DaoKe(BaseExtractor):

    async def urls(self) -> [str]:
        return ['https://www.docip.net/data/free.json']

    async def parse(self, doc):
        html = doc.html()
        items = json.loads(html)
        for element in items['data']:
            ip_port = element['ip'].split(':')
            proxy_type = 'http' if int(element['proxy_type']) == 2 else 'https'
            yield {'ip': ip_port[0], 'port': ip_port[1], 'proxy_type': proxy_type, 'country': ''}
