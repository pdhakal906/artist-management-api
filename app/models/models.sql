CREATE TYPE gender_type AS ENUM ('male', 'female', 'other');

CREATE TYPE role_type AS ENUM ('super_admin', 'artist_manager', 'artist');

CREATE TYPE genre_type AS ENUM ('rnb', 'country', 'classic', 'rock', 'jazz');

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(500) NOT NULL,
    role role_type NOT NULL,
    phone  VARCHAR(20) NOT NULL,
    dob TIMESTAMP NOT NULL,
    gender gender_type NOT NULL,
    address VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS artist (
  id SERIAL PRIMARY KEY,
  user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
  first_release_year INTEGER NOT NULL,
  no_of_albums_released INTEGER NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS music(
  id SERIAL PRIMARY KEY,
  artist_id INTEGER REFERENCES artist(id) ON DELETE CASCADE,
  title VARCHAR(255) NOT NULL,
  album_name VARCHAR(255) NOT NULL,
  genre genre_type NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



-- Trigger function to auto-update `updated_at`
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for `users` table
CREATE TRIGGER trigger_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Triggers for `artist` table
CREATE TRIGGER trigger_artist_updated_at
BEFORE UPDATE ON artist
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Triggers for `music` table
CREATE TRIGGER trigger_music_updated_at
BEFORE UPDATE ON music
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();