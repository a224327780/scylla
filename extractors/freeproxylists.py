import re
from urllib.parse import unquote

from extractors.base import BaseExtractor


class FreeProxyLists(BaseExtractor):
    request_config = {
        'Cookie': 'hl=zh; userno=20230211-003390; from=direct; visited=2023%2F02%2F11%2017%3A17%3A46; pv=10'}

    async def urls(self) -> [str]:
        return ['https://www.freeproxylists.net/zh/']

    async def parse(self, doc):
        elements = doc('.DataGrid tr')
        for element in elements.items():
            element_td = element('td')
            ip_html = element_td.eq(0).text().strip()
            if 'IPDecode' not in ip_html:
                continue

            port = element_td.eq(1).text().strip()
            proxy_type = element_td.eq(2).text().strip()

            re_item = re.search(r'IPDecode\("([^"]+)"\)', ip_html)
            a_html = unquote(re_item.group(1))
            re_item = re.search('>([^<]+)', a_html)
            yield {'ip': re_item.group(1), 'port': port, 'proxy_type': proxy_type, 'is_cn': 0}
