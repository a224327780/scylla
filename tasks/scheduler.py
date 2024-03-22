import asyncio
import logging

from sanic import Sanic

from tasks.clean_fail import CleanFailTask
from tasks.country_ip import CountryIpTask
from tasks.fetch_ip import FetchIpTask
from tasks.validate_ip import ValidateIpTask
from tasks.validate_mjj import ValidateMjj


class Scheduler:

    @classmethod
    async def run(cls, app: Sanic):
        request_session = app.ctx.request_session
        logger = logging.getLogger('sanic.root')

        # 验证ip-mjj
        # validate_ip_mjj_task = app.add_task(ValidateMjj.run(request_session))
        # logger.debug(validate_ip_mjj_task)

        # 验证ip
        validate_ip_task = app.add_task(ValidateIpTask.run(request_session, app.config.VALIDATE_PROXY_TIME))
        logger.debug(validate_ip_task)

        # 删除验证失败
        clean_fail_ip_task = app.add_task(CleanFailTask.run(request_session))
        logger.debug(clean_fail_ip_task)

        # 更新ip地区
        update_ip_country_task = app.add_task(CountryIpTask.run(request_session, 600))
        logger.debug(update_ip_country_task)

        # 获取ip
        fetch_ip_task = app.add_task(FetchIpTask.run(request_session))
        logger.debug(fetch_ip_task)

    @classmethod
    async def shutdown(cls):
        tasks = []
        for task in asyncio.all_tasks():
            if task is not asyncio.current_task():
                tasks.append(task)
                task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
