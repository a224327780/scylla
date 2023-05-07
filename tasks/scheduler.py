import asyncio

from sanic import Sanic

from tasks.clean_fail import CleanFailTask
from tasks.country_ip import CountryIpTask
from tasks.fetch_ip import FetchIpTask
from tasks.validate_ip import ValidateIpTask


class Scheduler:

    @classmethod
    async def run(cls, app: Sanic):
        request_session = app.ctx.request_session
        db = app.ctx.db

        # 获取ip
        fetch_ip_task = FetchIpTask.run(request_session, db)
        asyncio.ensure_future(fetch_ip_task)

        await asyncio.sleep(1)

        # 验证ip
        validate_ip_task = ValidateIpTask.run(request_session, db, 120)
        asyncio.ensure_future(validate_ip_task)

        # 删除验证失败
        asyncio.ensure_future(CleanFailTask.run(request_session, db))

        # 更新ip地区
        asyncio.ensure_future(CountryIpTask.run(request_session, db, 600))

    @classmethod
    async def shutdown(cls):
        tasks = []
        for task in asyncio.all_tasks():
            if task is not asyncio.current_task():
                tasks.append(task)
                task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
