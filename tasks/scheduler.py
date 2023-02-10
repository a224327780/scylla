import pyquery

from tasks.base.spider import Spider
from utils.common import get_extractors


class Scheduler(Spider):

    async def process_start_urls(self):
        async for (name, extractor) in get_extractors():
            urls = await extractor.urls()
            for url in urls:
                if 'jiangxianli' in url:
                    yield self.request(url=url, callback=self.parse, metadata=extractor)

    async def parse(self, response, extractor):
        html = await response.text()
        doc = pyquery.PyQuery(html)
        async for item in extractor.parse(doc):
            print(item)

    async def run(self):
        await self.start_master()
