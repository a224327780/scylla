import os
from cloudant.client import Cloudant
from cloudant.result import Result, ResultByKey

class DB:
    client = None
    db = None

    @classmethod
    def init_db(cls, loop, db_name='scylla'):
        pasword = os.getenv('DB_PASSWORD')
        username = os.getenv('DB_USERNAME', 'admin')
        host = os.getenv('DB_HOST', 'https://couchdb-atcooc123.cloud.okteto.net')
        cls.client = Cloudant(username, pasword, url=host, connect=True, use_basic_auth=True)
        cls.db = cls.client.create_database(db_name)

    @classmethod
    def get_db(cls, db_name=None):
        return cls.client[db_name] if db_name else cls.db

    @classmethod
    def save(cls, data):
        return cls.db.create_document(data)

    @classmethod
    def close_db(cls):
        if cls.client:
            cls.client.disconnect()
