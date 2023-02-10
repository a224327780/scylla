from tasks.extractors.base import BaseExtractor


class FreeProxyList(BaseExtractor):

    async def urls(self) -> [str]:
        return ['https://free-proxy-list.net/']

    async def parse(self, document):
        pass
