from tasks.base import BaseTask
from utils.common import get_bj_date


class CleanFailTask(BaseTask):

    async def process_start_urls(self):
        yield []

    async def after_start_worker(self):
        d = get_bj_date(-3600 * 24 * 2)
        cond = {'status': 2, 'fail_count': {'$gte': 2}, 'last_time': {'$lt': d}}
        async for item in self.col.find(cond).limit(1000):
            await self.col.delete_one({'_id': item['_id']})
            self.logger.info(f'delete fail ip: {item["_id"]}')
