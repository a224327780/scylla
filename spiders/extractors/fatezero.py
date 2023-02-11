import ujson

from spiders.extractors.base import BaseExtractor


class FateZero(BaseExtractor):

    async def urls(self) -> [str]:
        return ['http://proxylist.fatezero.org/proxy.list']

    async def parse(self, document):
        html = document.html()
        items = html.split('\n')
        for item in items:
            try:
                data = ujson.loads(item)
                is_cn = 1 if data['country'] in ['CN', 'HK'] else 0
                yield {'ip': data['host'], 'port': data['port'], 'proxy_type': data['type'], 'is_cn': is_cn}
            except Exception as e:
                print(e, item)
