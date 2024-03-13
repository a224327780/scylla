from extractors.base import BaseExtractor


class FreeProxyWord(BaseExtractor):

    async def urls(self) -> [str]:
        return ['https://www.freeproxy.world']

    async def parse(self, doc):
        elements = doc('.layui-table tbody tr')
        for element in elements.items():
            element_td = element('td')
            ip = element_td.eq(0).text().strip()
            port = element_td.eq(1).text().strip()
            proxy_type = element_td.eq(5).text().strip()
            if not port:
                continue
            yield {'ip': ip, 'port': port, 'proxy_type': proxy_type}
