from tasks.extractors.base import BaseExtractor


class HideMy(BaseExtractor):

    async def urls(self) -> [str]:
        return ['https://api.proxyscrape.com/proxytable.php?nf=true&country=all']

    async def parse(self, document):
        pass
