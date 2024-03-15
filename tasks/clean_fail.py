from tasks.base import BaseTask


class CleanFailTask(BaseTask):

    async def process_start_urls(self):
        yield []

    async def after_start_worker(self):
        async for item in self.col.find({'status': 2, 'fail_count': {'$gte': 2}}).sort('last_time', -1).limit(200):
            await self.col.delete_one({'_id': item['_id']})
            self.logger.info(f'delete fail ip: {item["_id"]}')
