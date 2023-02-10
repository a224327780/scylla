import os
import dotenv

dotenv.load_dotenv()

FORWARDED_SECRET = '23bd9d81dc7c6e7b6ad103f1343979ab'
REAL_IP_HEADER = 'X-Real-IP'
PROXIES_COUNT = 1

MONGO_URI = os.getenv('MONGO_URI', '')
REDIS_URI = os.getenv('REDIS_URI', '')
ENV = os.getenv('ENV', 'PROD')
DEV = ENV == 'DEV'
PROD = ENV == 'PROD'
