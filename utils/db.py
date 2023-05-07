from pathlib import Path
from sqlite3 import IntegrityError

import aiosqlite


class DB:
    client = None

    def __init__(self, loop=None):
        self.table_name = 'scylla'

    async def conn(self):
        db_file = Path(__file__).parent.parent / 'data.db'
        self.client = await aiosqlite.connect(db_file)
        self.client.row_factory = aiosqlite.Row

    async def insert(self, data: dict):
        columns = ', '.join(data.keys())
        placeholders = ', '.join('?' * len(data))
        sql = f'INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})'
        values = [int(x) if isinstance(x, bool) else x for x in data.values()]
        try:
            await self.client.execute(sql, values)
            await self.client.commit()
        except IntegrityError:
            pass

    async def update(self, _id, data: dict):
        columns = ', '.join('{} = ?'.format(k) for k in data)
        sql = f'UPDATE {self.table_name} SET {columns} where id = ?'
        values = list(data.values())
        values.append(_id)
        await self.client.execute(sql, values)
        await self.client.commit()

    async def get_pending_validation(self, limit=200):
        async for row in self.query('', limit=limit, order_by='status asc, last_time asc'):
            yield row

    async def get_country_empty(self, limit=50):
        where = "status = 1 and country = ''"
        async for row in self.query(where, limit=limit):
            yield row

    async def get_fail(self, limit=200):
        where = 'status = 2 and fail_count >= 3'
        async for row in self.query(where, limit=limit, fields='id'):
            yield row

    async def query(self, where, order_by=None, fields=None, limit=50, offset=0, group_by=None):
        if fields is None:
            fields = '*'

        order = f' order by {order_by}' if order_by else ''
        group = f' group by {group_by}' if group_by else ''
        sql = f"SELECT {fields} FROM {self.table_name} where {where}{order}{group} limit {offset}, {limit}"
        async with self.client.execute(sql) as cursor:
            async for row in cursor:
                yield row

    async def delete(self, _id):
        sql = f'DELETE FROM {self.table_name} where id = ?'
        await self.client.execute(sql, (_id,))
        await self.client.commit()

    async def close(self):
        if self.client:
            await self.client.close()
