import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SERVER_HOST = os.getenv("SERVER_HOST") or "localhost"
    SERVER_PORT = int(os.getenv("SERVER_PORT") or 3)
    MAX_CONNECTIONS = int(os.getenv("MAX_CONNECTIONS") or 1000)
    MAX_CONNECTION_PER_CLIENT = int(os.getenv("MAX_CONNECTION_PER_CLIENT") or 1)
    CONCURRENT_CONTROL_REDIS_KEY = (
        os.getenv("CONCURRENT_CONTROL_REDIS_KEY") or "concurrency_control"
    )
    REDIS_HOST = os.getenv("REDIS_HOST")
    REDIS_PORT = int(os.getenv("REDIS_PORT") or 6379)
