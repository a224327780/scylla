import asyncio
import logging
from asyncio import iscoroutinefunction, coroutines
from types import AsyncGeneratorType
from typing import Optional

from aiohttp import ClientSession, TCPConnector

from utils.db import DB


class BaseTask:
    concurrency = 10
    worker_tasks = []
    request_session: Optional[ClientSession] = None
    close_request_session = False
    col = None

    @classmethod
    async def run(cls, request_session, wait_for=3600):
        ins = cls()
        ins.request_session = request_session
        ins.col = DB.get_col()
        await ins.start_worker(wait_for)

    def __init__(self):
        self.sem = asyncio.Semaphore(self.concurrency)
        self.worker = []
        self.logger = logging.getLogger('sanic.root')
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}

    async def process_start_urls(self):
        yield self.request('https://api.ipify.org/')

    async def after_start_worker(self):
        pass

    async def process_async_callback(self, callback_result: AsyncGeneratorType, response):
        async for each_callback in callback_result:
            self.logger.info(each_callback)

    async def start_worker(self, sleep=3600):
        work_name = self.__class__.__name__
        while True:
            try:
                self.logger.info(f'start {work_name}.')
                worker_tasks = []
                async for item in self.process_start_urls():
                    if coroutines.iscoroutine(item):
                        worker_tasks.append(item)

                if worker_tasks:
                    results = await asyncio.gather(
                        *worker_tasks, return_exceptions=True
                    )
                    for task_result in results:
                        if not isinstance(task_result, RuntimeError) and type(task_result) is tuple:
                            callback_result = task_result[0]
                            response = task_result[1]
                            if isinstance(callback_result, AsyncGeneratorType):
                                await self.process_async_callback(callback_result, response)
                        else:
                            self.logger.error(f'[{work_name}] <Error: {task_result}>')
                    await self.close_request()
                await self.after_start_worker()
                self.logger.info(f'[{work_name}]: Wait {sleep} seconds.')
                await asyncio.sleep(sleep)
            except Exception as e:
                self.logger.exception(e)

    @property
    def current_request_session(self):
        if self.request_session is None:
            self.request_session = ClientSession(connector=TCPConnector(ssl=False))
            self.close_request_session = True
        return self.request_session

    async def close_request(self):
        if self.close_request_session:
            await self.request_session.close()

    async def request(self, url: str, callback=None, metadata=None, **request_config):
        response = None
        try:
            async with self.sem:
                response = await self.fetch(url, **request_config)
                if response and not response.ok:
                    self.logger.warning(f"<Error: {url} {response.status}>")
        except asyncio.TimeoutError:
            self.logger.error(f"<Error: {url} Timeout> {request_config}")
        except Exception as e:
            self.logger.error(f"<Error: {url} {e}>")

        callback_result = None
        if callback is not None:
            try:
                if iscoroutinefunction(callback):
                    callback_result = await callback(response, metadata)
                else:
                    callback_result = callback(response, metadata)
            except Exception as e:
                self.logger.exception(e)
        return callback_result, response

    async def fetch(self, url: str, method='GET', **request_config):
        request_config.setdefault('ssl', False)
        request_config.setdefault('timeout', 20)
        request_config.setdefault('headers', self.headers)
        if 'data' in request_config or 'json' in request_config:
            method = 'POST'
        return await self.current_request_session.request(method, url, **request_config)
