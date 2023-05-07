import json

from extractors.base import BaseExtractor


class GeoNode(BaseExtractor):

    async def urls(self) -> [str]:
        return ['https://proxylist.geonode.com/api/proxy-list?limit=150&page=1&sort_by=lastChecked&sort_type=desc']

    async def parse(self, document):
        html = document.html()
        data = json.loads(html)
        for item in data['data']:
            country = item['country']
            is_cn = 1 if country in ['CN', 'HK'] else 0
            yield {'ip': item['ip'], 'port': item['port'], 'proxy_type': item['protocols'][0], 'is_cn': is_cn,
                   'country': country}
