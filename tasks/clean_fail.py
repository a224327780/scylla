from tasks.base import BaseTask


class CleanFailTask(BaseTask):

    async def process_start_urls(self):
        # cond = {'status': 2, 'country': {'$ne': ''}, 'fail_count': {'$lt': 3}}
        # async for item in self.col.find(cond).sort('last_time', 1).limit(300):
        #     data = self.get_start_url_data(item)
        #     yield self.request(url=data['validate_url'], callback=self.validate, metadata=data,
        #                        proxy=data['validate_url'], timeout=30)
        yield []

    async def after_start_worker(self):
        async for item in self.col.find({'status': 2, 'fail_count': {'$gte': 2}}).limit(500):
            await self.col.delete_one({'_id': item['_id']})
            self.logger.info(f'delete fail ip: {item["_id"]}')
