class BaseExtractor:
    request_config = {}
    name = None
    status = 1

    async def urls(self) -> [str]:
        raise NotImplementedError

    async def parse(self, doc):
        raise NotImplementedError

    def get_data_by_layui(self, element):
        element_td = element('td')
        ip = element_td.eq(0).text().strip()
        port = element_td.eq(1).text().strip()
        proxy_type = element_td.eq(4).text().strip()
        return {'ip': ip, 'port': port, 'proxy_type': proxy_type, 'country': ''}

