from db.database import connect_db
from asyncpg import InvalidTextRepresentationError
from auth.schemas.users import UserUpdate


async def create_user(
    first_name: str,
    last_name: str,
    email: str,
    password: str,
    role: str,
    phone: str,
    dob: str,
    gender: str,
    address: str,
):
    conn = await connect_db()
    try:
        user = await conn.fetchrow(
            """
            INSERT INTO users (first_name, last_name, email, password, role, phone, dob, gender, address)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9) RETURNING id, first_name, last_name, email, role, phone, dob, gender, address, created_at, updated_at
        """,
            first_name,
            last_name,
            email,
            password,
            role,
            phone,
            dob.replace(tzinfo=None),
            gender,
            address,
        )
        return user if user else None
    except InvalidTextRepresentationError as e:
        raise ValueError(str(e))

    finally:
        await conn.close()


async def get_user_by_email(email: str):
    conn = await connect_db()
    try:
        return await conn.fetchrow("SELECT * FROM users WHERE email = $1", email)
    finally:
        await conn.close()


async def get_user_by_id(user_id: int):
    conn = await connect_db()
    try:
        return await conn.fetchrow(
            "SELECT id,email,first_name,last_name,dob,role,phone,gender,address,created_at,updated_at FROM users WHERE id = $1",
            user_id,
        )
    finally:
        await conn.close()


async def get_users_count():
    conn = await connect_db()
    try:
        return await conn.fetchval("SELECT COUNT(*) FROM users")
    finally:
        await conn.close()


async def get_all_users(page: int, page_size: int):
    conn = await connect_db()
    try:
        offset = (page - 1) * 10
        query = """
          SELECT id, first_name, last_name, email, role, phone, dob, gender, address, created_at, updated_at
          FROM users
          ORDER BY id DESC
          LIMIT $1 OFFSET $2
      """
        return await conn.fetch(query, page_size, offset)
    finally:
        await conn.close()


async def update_user(user_id: int, user: UserUpdate):
    conn = await connect_db()

    try:

        update_fields = []
        values = []
        index = 1

        for key, value in user.model_dump(exclude_unset=True).items():
            update_fields.append(f"{key} = ${index}")
            values.append(value)
            index += 1

        values.append(user_id)

        query = f"""
            UPDATE users
            SET {', '.join(update_fields)}
            WHERE id = ${index}
            RETURNING id, first_name, last_name, email, role, phone, dob, gender, address, created_at, updated_at
        """

        updated_user = await conn.fetchrow(query, *values)
        return dict(updated_user) if updated_user else None

    finally:
        await conn.close()


async def delete_user(user_id: int):
    conn = await connect_db()

    try:

        query = f"""
           DELETE FROM users WHERE id = $1
        """
        await conn.execute(query, user_id)
        return
    finally:
        await conn.close()
