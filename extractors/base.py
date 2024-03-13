class BaseExtractor:
    request_config = {}
    name = None
    status = 1

    async def urls(self) -> [str]:
        raise NotImplementedError

    async def parse(self, doc):
        raise NotImplementedError
