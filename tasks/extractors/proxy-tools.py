from tasks.extractors.base import BaseExtractor


class ProxyTools(BaseExtractor):

    async def urls(self) -> [str]:
        return [f'https://cn.proxy-tools.com/proxy/us?page={i}' for i in range(1, 4)] + [
            f'https://cn.proxy-tools.com/proxy/cn?page={i}' for i in range(1, 3)]

    async def parse(self, document):
        pass
