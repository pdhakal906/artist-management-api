from db.database import connect_db


async def create_user(username: str, email: str, password_hash: str):
    conn = await connect_db()
    try:
        await conn.execute(
            """
            INSERT INTO users (username, email, password)
            VALUES ($1, $2, $3)
        """,
            username,
            email,
            password_hash,
        )
    finally:
        await conn.close()


async def get_user_by_email(email: str):
    conn = await connect_db()
    try:
        return await conn.fetchrow("SELECT * FROM users WHERE email = $1", email)
    finally:
        await conn.close()
