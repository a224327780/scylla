import json

from spiders.extractors.base import BaseExtractor


class ProxyScrape(BaseExtractor):

    async def urls(self) -> [str]:
        return ['https://api.proxyscrape.com/proxytable.php?nf=true&country=all']

    async def parse(self, document):
        html = document.html()
        data = json.loads(html)
        for _type in data:
            i = 0
            for k, v in data[_type].items():
                i += 1
                if i > 20:
                    break
                is_cn = 1 if v['country'] in ['CN', 'HK'] else 0
                host = k.split(':')
                yield {'ip': host[0], 'port': host[1], 'proxy_type': _type, 'is_cn': is_cn}
