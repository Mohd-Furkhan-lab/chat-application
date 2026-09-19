import redis
import os
from dotenv import load_dotenv

load_dotenv()

r = redis.from_url(os.getenv("redis_url"))