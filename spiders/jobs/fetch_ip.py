from pyquery import pyquery
from sanic.log import logger

from utils.common import get_item_proxy
from utils.db import DB


class FetchIpJob:

    @classmethod
    async def parse_ip(cls, response, extractor):
        if response is None:
            return

        html = await response.text()
        doc = pyquery.PyQuery(html)
        name = extractor.name
        async for item in extractor.parse(doc):
            item['name'] = name
            proxy = get_item_proxy(item)
            _id = proxy.pop('ip')
            proxy['_id'] = _id
            logger.info(f'[{name}] fetch ip: {_id} in queue.')
            DB.save(proxy)
