from spiders.extractors.base import BaseExtractor


class FreeProxyList(BaseExtractor):

    async def urls(self) -> [str]:
        return ['https://free-proxy-list.net/']

    async def parse(self, doc):
        elements = doc('.fpl-list tbody tr')
        for element in elements.items():
            element_td = element('td')
            ip = element_td.eq(0).text().strip()
            port = element_td.eq(1).text().strip()
            code = element_td.eq(2).text().strip().lower()
            proxy_type = 'https' if element_td.eq(6).text().strip() == 'yes' else 'http'
            if not port:
                continue
            is_cn = 1 if code in ['cn', 'hk'] else 0
            yield {'ip': ip, 'port': port, 'proxy_type': proxy_type, 'is_cn': is_cn}
