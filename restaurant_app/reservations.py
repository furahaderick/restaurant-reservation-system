"""Reservation and table availability operations."""

from datetime import datetime

from psycopg2.extras import RealDictCursor

from restaurant_app.cache import (
    cache_availability,
    clear_availability_cache,
    get_cached_availability,
    make_availability_key,
)
from restaurant_app.db import get_connection


def validate_booking(starts_at, ends_at, party_size):
    if not isinstance(party_size, int) or party_size < 1:
        raise ValueError("Party size must be a positive whole number.")
    if not isinstance(starts_at, datetime) or not isinstance(ends_at, datetime):
        raise TypeError("Start and end times must be datetime values.")
    if starts_at.tzinfo is None or ends_at.tzinfo is None:
        raise ValueError("Start and end times must include a timezone.")
    if ends_at <= starts_at:
        raise ValueError("End time must be after start time.")


def find_available_tables(restaurant_id, starts_at, ends_at, party_size):
    """Return available tables; cache results briefly in Redis."""
    validate_booking(starts_at, ends_at, party_size)
    key = make_availability_key(restaurant_id, starts_at, ends_at, party_size)
    cached = get_cached_availability(key)
    if cached is not None:
        return cached

    sql = """
        SELECT t.id, t.table_number, t.capacity
        FROM restaurant_tables AS t
        WHERE t.restaurant_id = %s
            AND t.capacity >= %s
            AND NOT EXISTS (
                SELECT 1
                FROM reservations AS r
                WHERE r.table_id = t.id
                AND r.status = 'confirmed'
                AND r.starts_at < %s
                AND r.ends_at > %s
            )
        ORDER BY t.capacity, t.id
    """
    with get_connection() as connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(sql, (restaurant_id, party_size, ends_at, starts_at))
            tables = [dict(row) for row in cursor.fetchall()]

    # datetime values aren't present in this result, so it is JSON serializable.
    cache_availability(key, tables)
    return tables


def book_reservation(restaurant_id, customer_id, starts_at, ends_at, party_size):
    """
    Book the smallest suitable free table.

    The transaction locks suitable table rows first. Other booking transactions
    must wait for those locks, and the conflict check runs after the lock is
    acquired. This prevents two simultaneous bookings from choosing the same
    table for overlapping times.
    """
    validate_booking(starts_at, ends_at, party_size)

    with get_connection() as connection:
        # Explicit transaction makes the booking all-or-nothing.
        try:
            with connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT id, capacity
                        FROM restaurant_tables
                        WHERE restaurant_id = %s AND capacity >= %s
                        ORDER BY capacity, id
                        FOR UPDATE
                        """,
                        (restaurant_id, party_size),
                    )
                    candidate_tables = cursor.fetchall()

                    selected_table_id = None
                    for table_id, capacity in candidate_tables:
                        cursor.execute(
                            """
                            SELECT 1
                            FROM reservations
                            WHERE table_id = %s
                                AND status = 'confirmed'
                                AND starts_at < %s
                                AND ends_at > %s
                            LIMIT 1
                            """,
                            (table_id, ends_at, starts_at),
                        )
                        if cursor.fetchone() is None:
                            selected_table_id = table_id
                            break

                    if selected_table_id is None:
                        raise ValueError(
                            "No suitable table is available for that time."
                        )

                    cursor.execute(
                        """
                        INSERT INTO reservations
                            (table_id, customer_id, starts_at, ends_at, party_size)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING id, table_id, customer_id, starts_at, ends_at, party_size, status
                        """,
                        (
                            selected_table_id,
                            customer_id,
                            starts_at,
                            ends_at,
                            party_size,
                        ),
                    )
                    row = cursor.fetchone()
                    reservation = {
                        "id": row[0],
                        "table_id": row[1],
                        "customer_id": row[2],
                        "starts_at": row[3].isoformat(),
                        "ends_at": row[4].isoformat(),
                        "party_size": row[5],
                        "status": row[6],
                    }
        except Exception:
            # psycopg2's connection context rolls back when an exception occurs.
            raise

    clear_availability_cache(restaurant_id)
    return reservation
