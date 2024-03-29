import copy
import ipaddress

import pyquery

from tasks.base import BaseTask
from utils.common import get_extractors, get_item_proxy


class FetchIpTask(BaseTask):
    proxy_count = 0

    async def process_start_urls(self):
        self.proxy_count = 0
        headers = copy.deepcopy(self.headers)
        async for (name, extractor) in get_extractors():
            extractor.name = name
            urls = await extractor.urls()
            if extractor.status != 1 or not urls:
                continue

            request_config = extractor.request_config
            if request_config:
                headers.update(request_config)

            for url in urls:
                yield self.request(url=url, callback=self.parse_ip, metadata=extractor, headers=headers)

    async def parse_ip(self, response, extractor):
        if response is None:
            return

        html = await response.text()
        doc = pyquery.PyQuery(html)
        name = extractor.name

        async for item in extractor.parse(doc):
            if not item.get('ip') or not item.get('port'):
                continue
            try:
                item['name'] = name
                proxy = get_item_proxy(item)
                _id = proxy.pop('ip')

                if ipaddress.ip_address(_id).is_private:
                    self.logger.warning(_id)
                    continue

                data = await self.col.find_one({'_id': _id})
                if data:
                    self.logger.warning(f'{_id} already exists')
                    continue

                proxy['_id'] = _id
                self.proxy_count += 1
                self.logger.info(f'[{name}] fetch ip: {_id} in queue.')
                await self.col.insert_one(proxy)
            except Exception as e:
                self.logger.error(f'[{name}] parse error: {e}\n{item}')

    async def after_start_worker(self):
        self.logger.info(f'fetch count ip: {self.proxy_count}')
