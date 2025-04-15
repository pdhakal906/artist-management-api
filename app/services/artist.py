from db.database import connect_db
from schemas.artist import (
    ArtistCreate,
    ArtistUpdate,
    PaginatedArtistResponse,
    ArtistOut,
)


async def create_artist(artist_data: ArtistCreate):
    conn = await connect_db()
    try:
        async with conn.transaction():
            # Insert the artist
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

            # Fetch artist + user info in flat structure
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


# async def get_all_artist(page: int, page_size: int):
#     conn = await connect_db()
#     try:
#         offset = (page - 1) * 10
#         query = """
#           SELECT * FROM artist ORDER BY id DESC LIMIT $1 OFFSET $2
#       """
#         return await conn.fetch(query, page_size, offset)
#     finally:
#         await conn.close()


async def get_all_artist(page: int, page_size: int):
    conn = await connect_db()
    try:
        offset = (page - 1) * page_size  # Use page_size instead of hardcoded 10
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


async def update_artist(artist_id: int, artist: ArtistUpdate):
    conn = await connect_db()
    try:
        async with conn.transaction():
            # Fetch user_id from artist
            artist_row = await conn.fetchrow(
                "SELECT user_id FROM artist WHERE id = $1", artist_id
            )
            if not artist_row:
                return None
            user_id = artist_row["user_id"]

            artist_fields = []
            artist_values = []
            user_fields = []
            user_values = []

            index = 1

            # Separate artist and user fields
            for key, value in artist.model_dump(exclude_unset=True).items():
                if key in {"first_release_year", "no_of_albums_released"}:
                    artist_fields.append(f"{key} = ${index}")
                    artist_values.append(value)
                    index += 1
                elif key in {"first_name", "last_name", "phone", "gender", "address"}:
                    user_fields.append(f"{key} = ${index}")
                    user_values.append(value)
                    index += 1

            # Update artist if needed
            if artist_fields:
                artist_values.append(artist_id)
                artist_query = f"""
                    UPDATE artist SET {', '.join(artist_fields)}
                    WHERE id = ${index}
                """
                await conn.execute(artist_query, *artist_values)
                index += 1

            # Update user if needed
            if user_fields:
                user_values.append(user_id)
                user_query = f"""
                    UPDATE users SET {', '.join(user_fields)}
                    WHERE id = ${index}
                """
                await conn.execute(user_query, *user_values)

            # Fetch and return updated artist + user data
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
            # Get user_id from artist
            user_row = await conn.fetchrow(
                "SELECT user_id FROM artist WHERE id = $1", artist_id
            )
            if not user_row:
                raise Exception("Artist not found")

            user_id = user_row["user_id"]

            # Delete the user (artist will be deleted due to ON DELETE CASCADE)
            await conn.execute("DELETE FROM users WHERE id = $1", user_id)

    finally:
        await conn.close()
