import logging
import os
import platform
import ssl

import aiomysql
from pymysql import DatabaseError, IntegrityError

platform_name = platform.system()
if platform_name == 'Linux':
    ssl_file = '/etc/ssl/certs/ca-certificates.crt'
elif 'Win' in platform_name:
    ssl_file = 'cacert.pem'
else:
    ssl_file = '/etc/ssl/cert.pem'

ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ctx.load_verify_locations(cafile=ssl_file)


class DB:
    pool = None

    def __init__(self, loop=None):
        self.table_name = 'scylla'
        self.loop = loop
        self.logger = logging.getLogger('sanic.root')

    async def conn(self):
        conn_params = {
            'host': os.getenv('DB_HOST', 'aws.connect.psdb.cloud'),
            'user': os.getenv('DB_USER', 'i8d54r063op9abhgerei'),
            'password': os.getenv('DB_PASSWORD', ''),
            'db': os.getenv('DB_NAME', 'db0'),
            'port': int(os.getenv('DB_PORT', 3306)),
            'cursorclass': aiomysql.cursors.DictCursor,
            'charset': 'utf8mb4',
        }
        self.pool = await aiomysql.create_pool(loop=self.loop, ssl=ctx, **conn_params)

    async def insert(self, data: dict):
        sqlcmd = (
            f"INSERT INTO {self.table_name} ({', '.join(data.keys())}) "
            f"VALUES (%({')s, %('.join(data.keys())})s)")
        return await self.execute(sqlcmd, data)

    async def batch_insert(self, data: list):
        sqlcmd = (
            f"INSERT INTO {self.table_name} ({', '.join(data[0].keys())}) "
            f"VALUES (%({')s, %('.join(data[0].keys())})s)")
        return await self.execute(sqlcmd, data)

    async def update(self, _id, data: dict):
        columns = ', '.join('{} = %s'.format(k) for k in data)
        sql = f'UPDATE {self.table_name} SET {columns} where id = %s'
        values = list(data.values())
        values.append(_id)
        return await self.execute(sql, values)

    async def query(self, where=None, order_by=None, fields=None, limit=50, offset=0, group_by=None):
        if fields is None:
            fields = '*'
        if where is None:
            where = '1 = 1'

        order = f' order by {order_by}' if order_by else ''
        group = f' group by {group_by}' if group_by else ''
        sql = f"SELECT {fields} FROM {self.table_name} where {where}{order}{group} limit {offset}, {limit}"
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.execute(sql)
                    async for row in cur:
                        yield row
                except DatabaseError as e:
                    self.logger.error(f"<Error: {sql} {e}>")

    async def delete(self, _id):
        sql = f'DELETE FROM {self.table_name} where id = %s'
        return await self.execute(sql, (_id,))

    async def execute(self, sql, values=None):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    if 'insert' in sql and values and type(values) == list:
                        await cur.executemany(sql, values)
                    else:
                        await cur.execute(sql, values)

                    await conn.commit()
                    if 'insert' in sql:
                        return cur.lastrowid
                    if 'update' in sql or 'delete' in sql:
                        return cur.rowcount
                except IntegrityError:
                    pass
                except Exception as e:
                    self.logger.error(f"<Error: {e}\n {sql}\n{values}>")
                return None

    async def close(self):
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
