import asyncio
import logging
from aiohttp import ClientSession
from aiosocksy.connector import ProxyConnector, ProxyClientRequest
from sanic import Sanic

from tasks.clean_fail import CleanFailTask
from tasks.country_ip import CountryIpTask
from tasks.fetch_ip import FetchIpTask
from tasks.validate_ip import ValidateIpTask


class Scheduler:

    @classmethod
    async def run(cls, app: Sanic):
        logger = logging.getLogger('sanic.root')

        # 获取ip
        request_session = ClientSession(loop=app.loop)
        fetch_ip_task = app.add_task(FetchIpTask.run(request_session, 4200))
        logger.debug(fetch_ip_task)
    
        # 验证ip
        validate_ip_task = app.add_task(ValidateIpTask.run(None, app.config.VALIDATE_PROXY_TIME))
        logger.debug(validate_ip_task)

        # 删除验证失败
        clean_fail_ip_task = app.add_task(CleanFailTask.run(request_session, 3900))
        logger.debug(clean_fail_ip_task)

        # 更新ip地区
        update_ip_country_task = app.add_task(CountryIpTask.run(request_session, 600))
        logger.debug(update_ip_country_task)


    @classmethod
    async def shutdown(cls):
        tasks = []
        for task in asyncio.all_tasks():
            if task is not asyncio.current_task():
                tasks.append(task)
                task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
