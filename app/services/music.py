from db.database import connect_db
from schemas.music import (
    MusicCreate,
    MusicUpdate,
    PaginatedMusicResponse,
    MusicOut,
)


async def create_music(
    music_data: MusicCreate,
):
    conn = await connect_db()
    try:
        music = await conn.fetchrow(
            """
            INSERT INTO music (artist_id,title,album_name,genre)
            VALUES ($1, $2, $3, $4) RETURNING id, artist_id,title,album_name,genre, created_at, updated_at
        """,
            music_data.artist_id,
            music_data.title,
            music_data.album_name,
            music_data.genre,
        )
        return music if music else None
    finally:
        await conn.close()


async def get_music_by_id(id: int):
    conn = await connect_db()
    try:
        return await conn.fetchrow("SELECT * FROM music WHERE id = $1", id)
    finally:
        await conn.close()


async def get_music_by_artist_id(artist_id: int, page: int, page_size: int):
    conn = await connect_db()
    try:
        offset = (page - 1) * 10
        return await conn.fetch(
            "SELECT * FROM music WHERE artist_id = $1 ORDER BY id DESC LIMIT $2 OFFSET $3",
            artist_id,
            page_size,
            offset,
        )
    finally:
        await conn.close()


async def get_music_count():
    conn = await connect_db()
    try:
        return await conn.fetchval("SELECT COUNT(*) FROM music")
    finally:
        await conn.close()


async def get_music_by_artist_count(artist_id: int):
    conn = await connect_db()
    try:
        return await conn.fetchval(
            "SELECT COUNT(*) FROM music WHERE artist_id = $1", artist_id
        )
    finally:
        await conn.close()


async def get_all_music(page: int, page_size: int):
    conn = await connect_db()
    try:
        offset = (page - 1) * 10
        query = """
          SELECT * FROM music ORDER BY id DESC LIMIT $1 OFFSET $2
      """
        return await conn.fetch(query, page_size, offset)
    finally:
        await conn.close()


async def update_music(music_id: int, music: MusicUpdate):
    conn = await connect_db()

    try:

        update_fields = []
        values = []
        index = 1

        for key, value in music.model_dump(exclude_unset=True).items():
            update_fields.append(f"{key} = ${index}")
            values.append(value)
            index += 1

        values.append(music_id)

        query = f"""
            UPDATE music
            SET {', '.join(update_fields)}
            WHERE id = ${index}
            RETURNING id, artist_id, title, album_name, genre, created_at, updated_at
        """

        updated_music = await conn.fetchrow(query, *values)
        return dict(updated_music) if updated_music else None

    finally:
        await conn.close()


async def delete_music(music_id: int):
    conn = await connect_db()

    try:

        query = f"""
           DELETE FROM music WHERE id = $1
        """
        await conn.execute(query, music_id)
        return
    finally:
        await conn.close()


async def get_music_page_data():
    conn = await connect_db()
    try:
        query = """
            SELECT 
                artist.id AS artist_id,
                users.first_name,
                users.last_name
            FROM artist
            JOIN users ON users.id = artist.user_id
        """
        return await conn.fetch(query)
    finally:
        await conn.close()
