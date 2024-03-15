from extractors.base import BaseExtractor


class LiuJiu(BaseExtractor):

    async def urls(self) -> [str]:
        return [f'https://www.69ip.cn/?page={i}' for i in range(1, 3)]

    async def parse(self, doc):
        elements = doc('.layui-table tr')
        for element in elements.items():
            element_td = element('td')
            yield self.get_data_by_layui(element_td)
