from spiders.extractors.base import BaseExtractor


class HideMy(BaseExtractor):
    request_config = {'Cookie': 't=296843518'}

    async def urls(self) -> [str]:
        return ['https://hidemy.name/en/proxy-list/']

    async def parse(self, doc):
        elements = doc('.table_block tbody tr')
        for element in elements.items():
            element_td = element('td')
            ip = element_td.eq(0).text().strip()
            port = element_td.eq(1).text().strip()
            country = element_td.eq(2).text().strip()
            proxy_type = element_td.eq(4).text().strip()
            if not port:
                continue
            is_cn = 1 if country == 'China' else 0
            yield {'ip': ip, 'port': port, 'proxy_type': proxy_type, 'is_cn': is_cn}
