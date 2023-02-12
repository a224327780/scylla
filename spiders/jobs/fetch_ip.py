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
        col = DB.get_col()
        name = extractor.__class__.__name__
        async for item in extractor.parse(doc):
            item['name'] = name
            proxy = get_item_proxy(item)
            _id = proxy.pop('ip')

            if not await col.find_one({'_id': _id}):
                proxy['_id'] = _id
                await col.insert_one(proxy)
                logger.info(f'[{name}] fetch ip: {_id} in queue.')
