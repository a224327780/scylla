from extractors.base import BaseExtractor


class JiangXianLi(BaseExtractor):

    async def urls(self) -> [str]:
        return []
        # return ['https://ip.jiangxianli.com/?page=1&country=%E4%B8%AD%E5%9B%BD']

    async def parse(self, doc):
        elements = doc('.layui-form .layui-table tbody tr')
        for element in elements.items():
            element_td = element('td')
            ip = element_td.eq(0).text().strip()
            port = element_td.eq(1).text().strip()
            proxy_type = element_td.eq(3).text().strip()
            if not port:
                continue
            is_cn = 1
            yield {'ip': ip, 'port': port, 'proxy_type': proxy_type, 'is_cn': is_cn}
