import re

from extractors.base import BaseExtractor


class Spys(BaseExtractor):

    async def urls(self) -> [str]:
        return ['https://spys.one/en/free-proxy-list/']

    async def parse(self, doc):
        elements = doc('tr[class^="spy1x"]')
        self.set_var(str(doc))
        for element in elements.items():
            e = element('.spy14').eq(0)
            if not e:
                continue

            td_1 = element('td').eq(1)
            td_3 = element('td').eq(3)
            country = td_3('a').attr('href').strip('/').split('/')[-1]
            data = e.text().split('document.write(')
            proxy_ip = data[0]
            data2 = re.findall(r'\(([^\\)]+)\)', data[1])
            port = []
            for item in data2:
                k, v = item.split('^')
                port.append('{}'.format(eval(f'{getattr(self, k)}^{getattr(self, v)}')))

            proxy_type = td_1('font.spy1').text().strip()
            proxy_type = re.sub(r'\(([^\\)]+)\)|\s', '', proxy_type).strip()
            proxy_port = int(''.join(port))
            yield {'ip': proxy_ip, 'port': proxy_port, 'proxy_type': proxy_type, 'country': country}

    def set_var(self, html):
        script = re.search(r'<script type="text/javascript">([\s\S]*?)</script>', html).group(1)
        for item in script.split(';'):
            if item and item.find('^') == -1:
                k, v = item.split('=')
                setattr(self, k, v)

        for item in script.split(';'):
            if item and item.find('^') != -1:
                a = item.split('=')
                k, v = a[1].split('^')
                setattr(self, a[0], eval(f'{k}^{getattr(self, v)}'))