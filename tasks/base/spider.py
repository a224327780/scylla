import asyncio
from asyncio import iscoroutinefunction

import async_timeout
from aiohttp import ClientSession
from sanic.log import logger


class Spider:
    concurrency = 10
    worker_tasks = []

    def __init__(self):
        self.request_queue = asyncio.Queue()
        self.sem = asyncio.Semaphore(self.concurrency)
        self.request_session = ClientSession()

    async def process_start_urls(self):
        raise NotImplementedError

    async def start_master(self):
        async for request_ins in self.process_start_urls():
            self.request_queue.put_nowait(request_ins)
        asyncio.ensure_future(self.start_worker())
        await self.request_queue.join()

    async def start_worker(self):
        while True:
            request_item = await self.request_queue.get()
            self.worker_tasks.append(request_item)
            if self.request_queue.empty():
                results = await asyncio.gather(
                    *self.worker_tasks, return_exceptions=True
                )
                # for task_result in results:
                #     if not isinstance(task_result, RuntimeError) and task_result:
                #         callback_result = task_result[0]
                #         request: Request = task_result[1]
                #         if isinstance(callback_result, AsyncGeneratorType):
                #             await self._process_async_callback(
                #                 callback_result, task_result[2]
                #             )
                #         await request.close_request()

                self.worker_tasks = []
            self.request_queue.task_done()

    async def request(self, url: str, callback=None, metadata=None, **request_config):
        try:
            async with self.sem:
                response = await self.fetch(url, **request_config)
            if callback is not None:
                if iscoroutinefunction(callback):
                    callback_result = await callback(response, metadata)
                else:
                    callback_result = callback(response, metadata)
            else:
                callback_result = None
            return callback_result, response
        except Exception as e:
            logger.error(f"<Error: {url} {e}>")
            return None, None

    async def fetch(self, url: str, method='GET', **request_config):
        timeout = request_config.pop("TIMEOUT", 20)
        request_config.setdefault('ssl', False)
        async with async_timeout.timeout(timeout):
            request_func = self.request_session.request(method, url, **request_config)
            resp = await request_func
        return resp
