from tasks.base import BaseTask


class CleanFailTask(BaseTask):

    async def process_start_urls(self):
        where = 'status = 2 and fail_count >= 3'
        async for item in self.db.query(where, limit=200, fields='id'):
            await self.db.delete(item['id'])
            self.logger.info(f'delete fail ip: {item["id"]}')
        yield []
