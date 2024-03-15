import re

from extractors.base import BaseExtractor
from utils.common import b64


class ProxyListOrg(BaseExtractor):

    async def urls(self) -> [str]:
        return [f'https://proxy-list.org/english/index.php?p={i}' for i in range(1, 11)]

    async def parse(self, doc):
        elements = doc('div.table ul')
        for element in elements.items():
            li_proxy = element('li.proxy').text().strip()
            proxy_type = element('li.https').text().strip()
            li_proxy_re = re.search(r"Proxy\('([^']+)'\)", li_proxy)
            if li_proxy_re:
                proxy_str = b64(li_proxy_re.group(1))
                proxy_str = proxy_str.split(':')
                yield {'ip': proxy_str[0], 'port': proxy_str[1], 'proxy_type': proxy_type}
