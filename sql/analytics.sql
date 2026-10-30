-- 1. Rank restaurants by average score within each city.
SELECT
    r.city,
    r.name AS restaurant_name,
    ROUND(AVG(rv.rating)::numeric, 2) AS average_rating,
    RANK() OVER (
        PARTITION BY r.city
        ORDER BY AVG(rv.rating) DESC
    ) AS city_rank
FROM restaurants r
JOIN reviews rv ON rv.restaurant_id = r.id
GROUP BY r.id, r.city, r.name
ORDER BY r.city, city_rank;

-- 2. Find tables for a restaurant that can fit a party and have no overlapping schedules.
WITH suitable_tables AS (
    SELECT t.id, t.table_number, t.capacity
    FROM restaurant_tables t
    WHERE t.restaurant_id = 1
        AND t.capacity >= 4
)
SELECT st.id, st.table_number, st.capacity
FROM suitable_tables st
WHERE NOT EXISTS (
    SELECT 1
    FROM reservations res
    WHERE res.table_id = st.id
        AND res.status = 'confirmed'
        AND res.starts_at < TIMESTAMPTZ '2026-11-01 20:00:00+02'
        AND res.ends_at > TIMESTAMPTZ '2026-11-01 18:00:00+02'
)
ORDER BY st.capacity;

-- 3. Examine the query plan.
EXPLAIN ANALYZE
SELECT t.id, t.table_number, t.capacity
FROM restaurant_tables t
WHERE t.restaurant_id = 1
  AND t.capacity >= 4
  AND NOT EXISTS (
      SELECT 1
      FROM reservations res
      WHERE res.table_id = t.id
        AND res.status = 'confirmed'
        AND res.starts_at < TIMESTAMPTZ '2026-11-01 20:00:00+02'
        AND res.ends_at > TIMESTAMPTZ '2026-11-01 18:00:00+02'
  )
ORDER BY t.capacity;

-- 4. Basic city/location search using any coordinates.
SELECT id, name, city, latitude, longitude
FROM restaurants
WHERE latitude BETWEEN -2.1 AND -1.8
  AND longitude BETWEEN 29.9 AND 30.2;
