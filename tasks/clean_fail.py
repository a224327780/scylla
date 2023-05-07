from tasks.base import BaseTask


class CleanFailTask(BaseTask):

    async def process_start_urls(self):
        async for item in self.db.get_fail():
            await self.db.delete(item['id'])
            self.logger.info(f'delete fail ip: {item["id"]}')
        yield []
