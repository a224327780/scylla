from extractors.base import BaseExtractor


class KaiXin(BaseExtractor):

    async def urls(self) -> [str]:
        return [f'http://www.kxdaili.com/dailiip/1/{i}.html' for i in range(1, 3)]

    async def parse(self, doc):
        elements = doc('table.active tr')
        for element in elements.items():
            element_td = element('td')
            ip = element_td.eq(0).text().strip()
            port = element_td.eq(1).text().strip()
            proxy_type = element_td.eq(3).text().split(',')[-1]
            yield {'ip': ip, 'port': port, 'proxy_type': proxy_type}
