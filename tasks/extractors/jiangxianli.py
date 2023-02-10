from tasks.extractors.base import BaseExtractor


class JiangXianLi(BaseExtractor):

    async def urls(self) -> [str]:
        return ['https://ip.jiangxianli.com/?page=1&country=%E4%B8%AD%E5%9B%BD']

    async def parse(self, doc):
        elements = doc('.layui-form .layui-table tbody tr')
        for element in elements.items():
            ip = element('td').eq(0).text().strip()
            port = element('td').eq(1).text().strip()
            proxy_type = element('td').eq(3).text().strip()
            if not port:
                continue
            is_cn = True
            yield {'ip': ip, 'port': int(port), 'proxy_type': proxy_type, 'is_cn': is_cn}
