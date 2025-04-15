import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


async def init_db():
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        with open("models/models.sql", "r") as f:
            sql = f.read()
        await conn.execute(sql)
        print("✅ Database initialized successfully.")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(init_db())
