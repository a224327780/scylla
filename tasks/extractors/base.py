class BaseExtractor:

    async def urls(self) -> [str]:
        raise NotImplementedError

    async def parse(self, doc):
        raise NotImplementedError
