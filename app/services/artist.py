from db.database import connect_db
from schemas.artist import (
    ArtistCreate,
    ArtistUpdate,
    PaginatedArtistResponse,
    ArtistOut,
)


async def create_artist(
    artist_data: ArtistCreate,
):
    conn = await connect_db()
    try:
        artist = await conn.fetchrow(
            """
            INSERT INTO artist (name,dob,gender,address,first_release_year,no_of_albums_released)
            VALUES ($1, $2, $3, $4, $5, $6) RETURNING id, name, dob, gender, address, first_release_year, no_of_albums_released, created_at, updated_at
        """,
            artist_data.name,
            artist_data.dob.replace(tzinfo=None),
            artist_data.gender,
            artist_data.address,
            artist_data.first_release_year,
            artist_data.no_of_albums_released,
        )
        return artist if artist else None
    finally:
        await conn.close()


async def get_artist_by_id(id: int):
    conn = await connect_db()
    try:
        return await conn.fetchrow("SELECT * FROM artist WHERE id = $1", id)
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
        offset = (page - 1) * 10
        query = """
          SELECT * FROM artist ORDER BY id LIMIT $1 OFFSET $2
      """
        return await conn.fetch(query, page_size, offset)
    finally:
        await conn.close()


async def update_user(artist_id: int, artist: ArtistUpdate):
    conn = await connect_db()

    try:

        update_fields = []
        values = []
        index = 1

        for key, value in artist.model_dump(exclude_unset=True).items():
            update_fields.append(f"{key} = ${index}")
            values.append(value)
            index += 1

        values.append(artist_id)

        query = f"""
            UPDATE artist
            SET {', '.join(update_fields)}
            WHERE id = ${index}
            RETURNING id, name, dob, gender, address, first_release_year, no_of_albums_released, created_at, updated_at
        """

        updated_artist = await conn.fetchrow(query, *values)
        return dict(updated_artist) if updated_artist else None

    finally:
        await conn.close()


async def delete_artist(artist_id: int):
    conn = await connect_db()

    try:

        query = f"""
           DELETE FROM artist WHERE id = $1
        """
        await conn.execute(query, artist_id)
        return
    finally:
        await conn.close()
