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
  name VARCHAR(255) NOT NULL,
  dob TIMESTAMP NOT NULL,
  gender gender_type NOT NULL,
  address VARCHAR(255) NOT NULL,
  first_release_year INTEGER NOT NULL,
  no_of_albums_released INTEGER NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS music(
  id SERIAL PRIMARY KEY,
  artist_id INTEGER REFERENCES artist(id),
  title VARCHAR(255) NOT NULL,
  album_name VARCHAR(255) NOT NULL,
  genre genre_type NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
