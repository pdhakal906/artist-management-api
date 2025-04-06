import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


async def connect_db():
    return await asyncpg.connect(DATABASE_URL)
