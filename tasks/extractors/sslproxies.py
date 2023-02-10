from tasks.extractors.base import BaseExtractor


class SslProxies(BaseExtractor):

    async def urls(self) -> [str]:
        return ['https://www.sslproxies.org/']

    async def parse(self, document):
        pass
