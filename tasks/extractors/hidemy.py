from tasks.extractors.base import BaseExtractor


class HideMy(BaseExtractor):

    async def urls(self) -> [str]:
        return ['https://hidemy.name/en/proxy-list/']

    async def parse(self, document):
        pass
