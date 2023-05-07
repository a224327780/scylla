from extractors.base import BaseExtractor


class FreeProxy(BaseExtractor):

    async def urls(self) -> [str]:
        return [
            f'https://www.freeproxy.world/?type=&anonymity=&country=&speed=&port=&page={i}' for i in range(1, 3)
        ]

    async def parse(self, doc):
        elements = doc('.layui-table tbody tr')
        for element in elements.items():
            element_td = element('td')
            ip = element_td.eq(0).text().strip()
            port = element_td.eq(1).text().strip()
            country = element_td.eq(2).text().strip()
            proxy_type = element_td.eq(5).text().strip()
            is_cn = 1 if country == 'China' else 0
            yield {'ip': ip, 'port': port, 'proxy_type': proxy_type, 'is_cn': is_cn}
