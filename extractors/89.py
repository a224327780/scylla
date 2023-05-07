from extractors.base import BaseExtractor


class BaJiu(BaseExtractor):

    async def urls(self) -> [str]:
        return []
        # return [
        #     f'https://www.89ip.cn/index_{i}.html' for i in range(1, 3)
        # ]

    async def parse(self, doc):
        elements = doc('.fly-panel tbody tr')
        for element in elements.items():
            element_td = element('td')
            ip = element_td.eq(0).text().strip()
            port = element_td.eq(1).text().strip()
            proxy_type = 'http'
            is_cn = 1
            yield {'ip': ip, 'port': port, 'proxy_type': proxy_type, 'is_cn': is_cn}
