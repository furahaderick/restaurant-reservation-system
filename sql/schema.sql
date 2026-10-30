-- PostgreSQL schema for the Restaurant Reservation and Review System.
-- Each table represents one main type of data.

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS restaurants (
    id SERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    city VARCHAR(80) NOT NULL,
    address TEXT NOT NULL,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    menu JSONB NOT NULL DEFAULT '[]'::jsonb,
    opening_hours JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(120) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS restaurant_tables (
    id SERIAL PRIMARY KEY,
    restaurant_id INTEGER NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    table_number VARCHAR(20) NOT NULL,
    capacity INTEGER NOT NULL CHECK (capacity > 0),
    UNIQUE (restaurant_id, table_number)
);

CREATE TABLE IF NOT EXISTS reservations (
    id SERIAL PRIMARY KEY,
    table_id INTEGER NOT NULL REFERENCES restaurant_tables(id),
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    starts_at TIMESTAMPTZ NOT NULL,
    ends_at TIMESTAMPTZ NOT NULL,
    party_size INTEGER NOT NULL CHECK (party_size > 0),
    status VARCHAR(20) NOT NULL DEFAULT 'confirmed'
        CHECK (status IN ('confirmed', 'cancelled')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (ends_at > starts_at)
);

CREATE TABLE IF NOT EXISTS reviews (
    id SERIAL PRIMARY KEY,
    restaurant_id INTEGER NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    short_comment TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (restaurant_id, customer_id)
);

-- Useful indexes for the core availability and reporting queries.
CREATE INDEX IF NOT EXISTS idx_tables_restaurant_capacity
    ON restaurant_tables (restaurant_id, capacity);

CREATE INDEX IF NOT EXISTS idx_reservations_table_time
    ON reservations (table_id, starts_at, ends_at)
    WHERE status = 'confirmed';

CREATE INDEX IF NOT EXISTS idx_reviews_restaurant_rating
    ON reviews (restaurant_id, rating);

CREATE INDEX IF NOT EXISTS idx_restaurants_city
    ON restaurants (city);

-- Optional location index. Enable PostGIS separately before using a proper
-- geography/GiST index; this basic project keeps latitude/longitude simple.
