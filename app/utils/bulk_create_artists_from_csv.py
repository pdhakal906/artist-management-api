import csv
from io import StringIO
from passlib.hash import bcrypt
from datetime import datetime
from fastapi import UploadFile
from db.database import connect_db


async def bulk_create_artists_from_csv(file: UploadFile):
    content = await file.read()
    text_stream = StringIO(content.decode("utf-8"))
    reader = csv.DictReader(text_stream)

    conn = await connect_db()
    artists = []
    try:
        async with conn.transaction():
            for row in reader:
                hashed_password = bcrypt.hash(row["password"])
                user = await conn.fetchrow(
                    """
                    INSERT INTO users (
                        first_name, last_name, email, password, role, phone, dob, gender, address
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                    RETURNING id, created_at, updated_at
                """,
                    row["first_name"],
                    row["last_name"],
                    row["email"],
                    hashed_password,
                    "artist",
                    row["phone"],
                    datetime.fromisoformat(row["dob"]),
                    row["gender"],
                    row["address"],
                )

                if not user:
                    continue

                user_id = user["id"]
                user_created_at = user["created_at"]
                user_updated_at = user["updated_at"]

                artist = await conn.fetchrow(
                    """
                    INSERT INTO artist (user_id, first_release_year, no_of_albums_released)
                    VALUES ($1, $2, $3)
                    RETURNING id, first_release_year, no_of_albums_released, created_at, updated_at
                """,
                    user_id,
                    int(row["first_release_year"]),
                    int(row["no_of_albums_released"]),
                )

                artists.append(
                    {
                        "id": artist["id"],
                        "user_id": user_id,
                        "first_release_year": artist["first_release_year"],
                        "no_of_albums_released": artist["no_of_albums_released"],
                        "created_at": artist["created_at"],
                        "updated_at": artist["updated_at"],
                        "user_created_at": user_created_at,
                        "user_updated_at": user_updated_at,
                        "user": {
                            "first_name": row["first_name"],
                            "last_name": row["last_name"],
                            "email": row["email"],
                            "phone": row["phone"],
                            "dob": row["dob"],
                            "gender": row["gender"],
                            "address": row["address"],
                            "role": "artist",
                        },
                    }
                )

        return artists
    finally:
        await conn.close()
