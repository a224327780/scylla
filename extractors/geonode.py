import json

from extractors.base import BaseExtractor


class GeoNode(BaseExtractor):

    async def urls(self) -> [str]:
        api = 'https://proxylist.geonode.com/api/proxy-list'
        return [f'{api}?filterUpTime=90&limit=300&page=1&sort_by=lastChecked&sort_type=desc']

    async def parse(self, document):
        html = document.html()
        data = json.loads(html)
        for item in data['data']:
            country = item['country']
            yield {'ip': item['ip'], 'port': item['port'], 'proxy_type': item['protocols'][0],
                   'country': country}
