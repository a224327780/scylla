import asyncio

from tasks.base import BaseTask


class CleanFailTask(BaseTask):

    async def start_worker(self, sleep=3600):
        while True:
            async for item in self.col.find({'status': 2, 'fail_count': {'$gte': 3}}).limit(200):
                await self.col.delete_one({'_id': item['_id']})
                self.logger.info(f'delete fail ip: {item["id"]}')
            await asyncio.sleep(sleep)
