from db.database import connect_db
from schemas.artist import (
    ArtistCreate,
    ArtistUpdate,
)


async def create_artist(artist_data: ArtistCreate):
    conn = await connect_db()
    try:
        async with conn.transaction():
            inserted_artist = await conn.fetchrow(
                """
                INSERT INTO artist (user_id, first_release_year, no_of_albums_released)
                VALUES ($1, $2, $3)
                RETURNING id
                """,
                artist_data.user_id,
                artist_data.first_release_year,
                artist_data.no_of_albums_released,
            )

            if not inserted_artist:
                return None

            artist_id = inserted_artist["id"]

            artist_with_user = await conn.fetchrow(
                """
                SELECT
                    artist.id,
                    artist.user_id,
                    artist.first_release_year,
                    artist.no_of_albums_released,
                    artist.created_at,
                    artist.updated_at,
                    users.first_name,
                    users.last_name,
                    users.email,
                    users.phone,
                    users.dob,
                    users.gender,
                    users.address,
                    users.role,
                    users.created_at AS user_created_at,
                    users.updated_at AS user_updated_at
                FROM artist
                JOIN users ON users.id = artist.user_id
                WHERE artist.id = $1
                """,
                artist_id,
            )

            return dict(artist_with_user)

    finally:
        await conn.close()


async def get_artist_by_id(id: int):
    conn = await connect_db()
    try:
        query = """
            SELECT
                artist.id,
                artist.user_id,
                artist.first_release_year,
                artist.no_of_albums_released,
                artist.created_at,
                artist.updated_at,

                users.first_name,
                users.last_name,
                users.email,
                users.phone,
                users.dob,
                users.gender,
                users.address,
                users.role,
                users.created_at AS user_created_at,
                users.updated_at AS user_updated_at

            FROM artist
            JOIN users ON users.id = artist.user_id
            WHERE artist.id = $1
        """
        return await conn.fetchrow(query, id)
    finally:
        await conn.close()


async def get_artists_count():
    conn = await connect_db()
    try:
        return await conn.fetchval("SELECT COUNT(*) FROM artist")
    finally:
        await conn.close()


async def get_all_artist(page: int, page_size: int):
    conn = await connect_db()
    try:
        offset = (page - 1) * page_size
        query = """
            SELECT 
                artist.*,
                users.first_name,
                users.last_name,
                users.email,
                users.phone,
                users.dob,
                users.gender,
                users.address,
                users.role,
                users.created_at AS user_created_at,
                users.updated_at AS user_updated_at
            FROM artist
            JOIN users ON artist.user_id = users.id
            ORDER BY artist.id DESC
            LIMIT $1 OFFSET $2
        """
        return await conn.fetch(query, page_size, offset)
    finally:
        await conn.close()


async def get_all_artists_without_pagination():
    conn = await connect_db()
    try:
        query = """
            SELECT 
                artist.id,
                artist.user_id,
                artist.first_release_year,
                artist.no_of_albums_released,
                artist.created_at,
                artist.updated_at,
                users.first_name,
                users.last_name,
                users.email,
                users.phone,
                users.dob,
                users.gender,
                users.address,
                users.role,
                users.created_at AS user_created_at,
                users.updated_at AS user_updated_at
            FROM artist
            JOIN users ON artist.user_id = users.id
            ORDER BY artist.id
        """
        return await conn.fetch(query)
    finally:
        await conn.close()


async def update_artist(artist_id: int, artist: ArtistUpdate):
    print(artist)
    conn = await connect_db()
    try:
        async with conn.transaction():
            artist_row = await conn.fetchrow(
                "SELECT user_id FROM artist WHERE id = $1", artist_id
            )
            if not artist_row:
                return None
            user_id = artist_row["user_id"]

            artist_data = []
            user_data = []

            for key, value in artist.model_dump(exclude_unset=True).items():
                if key in {"first_release_year", "no_of_albums_released"}:
                    artist_data.append((key, value))
                elif key in {"first_name", "last_name", "phone", "gender", "address"}:
                    user_data.append((key, value))

            if artist_data:
                artist_fields = [
                    f"{key} = ${i+1}" for i, (key, _) in enumerate(artist_data)
                ]
                artist_values = [value for _, value in artist_data]
                artist_values.append(artist_id)
                artist_query = f"""
                    UPDATE artist SET {', '.join(artist_fields)}
                    WHERE id = ${len(artist_values)}
                """
                await conn.execute(artist_query, *artist_values)

            if user_data:
                user_fields = [
                    f"{key} = ${i+1}" for i, (key, _) in enumerate(user_data)
                ]
                user_values = [value for _, value in user_data]
                user_values.append(user_id)
                user_query = f"""
                    UPDATE users SET {', '.join(user_fields)}
                    WHERE id = ${len(user_values)}
                """
                await conn.execute(user_query, *user_values)

            result = await conn.fetchrow(
                """
                SELECT
                    artist.id,
                    artist.user_id,
                    artist.first_release_year,
                    artist.no_of_albums_released,
                    artist.created_at,
                    artist.updated_at,
                    users.first_name,
                    users.last_name,
                    users.email,
                    users.phone,
                    users.dob,
                    users.gender,
                    users.address,
                    users.role,
                    users.created_at AS user_created_at,
                    users.updated_at AS user_updated_at
                FROM artist
                JOIN users ON users.id = artist.user_id
                WHERE artist.id = $1
                """,
                artist_id,
            )

            return dict(result)

    finally:
        await conn.close()


async def delete_artist(artist_id: int):
    conn = await connect_db()

    try:
        async with conn.transaction():
            user_row = await conn.fetchrow(
                "SELECT user_id FROM artist WHERE id = $1", artist_id
            )
            if not user_row:
                raise Exception("Artist not found")

            user_id = user_row["user_id"]
            await conn.execute("DELETE FROM users WHERE id = $1", user_id)

    finally:
        await conn.close()


async def get_artist_by_user_id(user_id: int):
    conn = await connect_db()
    try:
        query = """
            SELECT artist.id FROM artist JOIN users ON artist.user_id = users.id WHERE artist.user_id = $1
        """
        return await conn.fetchrow(query, user_id)
    finally:
        await conn.close()
