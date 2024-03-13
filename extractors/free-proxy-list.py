from extractors.base import BaseExtractor


class FreeProxyList(BaseExtractor):

    async def urls(self) -> [str]:
        return ['https://free-proxy-list.net/']

    async def parse(self, doc):
        elements = doc('.fpl-list tbody tr')
        for element in elements.items():
            element_td = element('td')
            ip = element_td.eq(0).text().strip()
            port = element_td.eq(1).text().strip()
            country = element_td.eq(2).text().strip().lower()
            proxy_type = 'https' if element_td.eq(6).text().strip() == 'yes' else 'http'
            if not port:
                continue
            yield {'ip': ip, 'port': port, 'proxy_type': proxy_type, 'country': country}
