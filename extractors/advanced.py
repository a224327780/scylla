import base64

from extractors.base import BaseExtractor


class Advanced(BaseExtractor):

    async def urls(self) -> [str]:
        return [f'https://advanced.name/freeproxy?page={i}' for i in range(1, 3)]

    async def parse(self, doc):
        elements = doc('#table_proxies tbody tr')
        for element in elements.items():
            element_td = element('td')
            ip = element_td.eq(1).attr('data-ip').strip()
            ip = base64.b64decode(ip.encode()).decode()
            port = element_td.eq(2).attr('data-port').strip()
            port = base64.b64decode(port.encode()).decode()

            country = element_td.eq(4).text().strip()
            proxy_type = element_td.eq(3).text().strip()
            for t in ['SOCKS5', 'HTTPS', 'HTTP', 'SOCKS4']:
                if t in proxy_type:
                    proxy_type = t
                    break

            yield {'ip': ip, 'port': port, 'proxy_type': proxy_type, 'country': country}
