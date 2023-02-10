import os

from motor.motor_asyncio import AsyncIOMotorClient


class DB:
    client = None
    db = None
    col = None

    @classmethod
    def init_db(cls, loop, db_name, col_name):
        mongo_uri = os.getenv('MONGO_URI')
        cls.client: AsyncIOMotorClient = AsyncIOMotorClient(mongo_uri, io_loop=loop)
        cls.db = cls.client[db_name]
        cls.col = cls.db[col_name]

    @classmethod
    def get_col(cls, col_name=None):
        return cls.db[col_name] if col_name else cls.col

    @classmethod
    def close_db(cls):
        cls.client.close()
