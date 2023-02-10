from tasks.extractors.base import BaseExtractor


class SocksProxy(BaseExtractor):

    async def urls(self) -> [str]:
        return ['https://www.socks-proxy.net/']

    async def parse(self, document):
        pass
