from tasks.extractors.base import BaseExtractor


class FreeProxy(BaseExtractor):

    async def urls(self) -> [str]:
        return [
            f'https://www.freeproxy.world/?type=&anonymity=&country=&speed=&port=&page={i}' for i in range(1, 3)
        ]

    async def parse(self, document):
        pass
