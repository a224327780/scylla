import asyncio
import logging
from asyncio import iscoroutinefunction

from aiohttp import ClientSession
from aiosocksy.connector import ProxyConnector, ProxyClientRequest
from sanic.log import logger


class Spider:
    concurrency = 10
    worker_tasks = []

    def __init__(self):
        self.request_queue = asyncio.Queue()
        self.sem = asyncio.Semaphore(self.concurrency)
        self.request_session = ClientSession(connector=ProxyConnector(), request_class=ProxyClientRequest)
        self.worker = []
        self.logger = logging.getLogger('sanic.root')

    async def start_worker(self, task_func, work_name, sleep=3600, callback=None):
        while True:
            self.logger.info(f'start {work_name}.')
            worker_tasks = []
            async for task in getattr(self, task_func)():
                worker_tasks.append(task)
            results = await asyncio.gather(
                *worker_tasks, return_exceptions=True
            )
            for task_result in results:
                if not isinstance(task_result, RuntimeError) and task_result:
                    if callback is not None:
                        await callback(task_result)
            self.logger.info(f'[{work_name}]: Wait {sleep} seconds.')
            await asyncio.sleep(sleep)

    async def request(self, url: str, callback=None, metadata=None, **request_config):
        try:
            async with self.sem:
                response = await self.fetch(url, **request_config)
        except asyncio.TimeoutError:
            response = None
            logger.error(f"<Error: {url} Timeout> ")
        except Exception as e:
            response = None
            logger.error(f"<Error: {url} {e}>")

        if callback is not None:
            if iscoroutinefunction(callback):
                callback_result = await callback(response, metadata)
            else:
                callback_result = callback(response, metadata)
        else:
            callback_result = None
        return callback_result, response

    async def fetch(self, url: str, method='GET', **request_config):
        request_config.setdefault('ssl', False)
        request_config.setdefault('timeout', 20)
        return await self.request_session.request(method, url, **request_config)

    async def cancel(self):
        for task in self.worker:
            task.cancel()
        await self.request_session.close()
