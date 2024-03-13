from extractors.base import BaseExtractor


class ProxyListDownload(BaseExtractor):

    async def urls(self) -> [str]:
        return [
            'https://www.proxy-list.download/api/v1/get?type=http',
        ]

    async def parse(self, doc):
        elements = doc.html().split('\n')
        for element in elements:
            element_td = element.split(':')
            if element_td and len(element_td) == 2:
                ip = element_td[0]
                port = element_td[1]
                yield {'ip': ip, 'port': port, 'proxy_type': 'http'}
