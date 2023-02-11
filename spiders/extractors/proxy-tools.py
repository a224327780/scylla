from spiders.extractors.base import BaseExtractor


class ProxyTools(BaseExtractor):

    async def urls(self) -> [str]:
        return []
        # return [f'https://cn.proxy-tools.com/proxy/us?page={i}' for i in range(1, 4)] + [
        #     f'https://cn.proxy-tools.com/proxy/cn?page={i}' for i in range(1, 3)]

    async def parse(self, doc):
        elements = doc('table tbody tr')
        for element in elements.items():
            element_td = element('td')
            ip = element_td.eq(0).text().strip()
            port = element_td.eq(1).text().strip()
            proxy_type = element_td.eq(2).text().strip()
            is_cn = 0
            yield {'ip': ip, 'port': port, 'proxy_type': proxy_type, 'is_cn': is_cn}
