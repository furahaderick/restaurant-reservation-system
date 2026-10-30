INSERT INTO restaurants (id, name, city, address, latitude, longitude, menu, opening_hours)
VALUES
(1, 'Kigali Garden', 'Kigali', 'KG 12 Ave, Kigali', -1.9441, 30.0619,
    '[{"name":"Grilled fish","price":8500},{"name":"Vegetable curry","price":6000}]',
    '{"monday":"09:00-22:00","tuesday":"09:00-22:00","sunday":"10:00-20:00"}'),
(2, 'Hillside Bistro', 'Kigali', 'KG 8 St, Kigali', -1.9536, 30.0606,
    '[{"name":"Beef burger","price":7000},{"name":"Pasta","price":6500}]',
    '{"monday":"10:00-23:00","tuesday":"10:00-23:00","sunday":"10:00-21:00"}'),
(3, 'Lake View Kitchen', 'Rubavu', 'Near Lake Kivu, Rubavu', -1.6773, 29.2604,
    '[{"name":"Tilapia","price":9000},{"name":"Chips","price":3000}]',
    '{"monday":"09:00-21:00","sunday":"09:00-20:00"}')
ON CONFLICT (id) DO NOTHING;

INSERT INTO customers (id, full_name, email)
VALUES
(1, 'Aline Uwase', 'aline@example.com'),
(2, 'Eric Niyonzima', 'eric@example.com'),
(3, 'Maya Ishimwe', 'maya@example.com')
ON CONFLICT (id) DO NOTHING;

INSERT INTO restaurant_tables (id, restaurant_id, table_number, capacity)
VALUES
(1, 1, 'A1', 2), (2, 1, 'A2', 4), (3, 1, 'A3', 6),
(4, 2, 'B1', 2), (5, 2, 'B2', 4), (6, 3, 'C1', 4)
ON CONFLICT (id) DO NOTHING;

INSERT INTO reviews (id, restaurant_id, customer_id, rating, short_comment)
VALUES
(1, 1, 1, 5, 'Lovely food'),
(2, 1, 2, 4, 'Friendly staff'),
(3, 2, 1, 4, 'Good atmosphere'),
(4, 2, 3, 3, 'Food was okay'),
(5, 3, 2, 5, 'Beautiful view')
ON CONFLICT (id) DO NOTHING;

-- Keep SERIAL counters correct after inserting explicit sample IDs.
SELECT setval(pg_get_serial_sequence('restaurants', 'id'), (SELECT MAX(id) FROM restaurants));
SELECT setval(pg_get_serial_sequence('customers', 'id'), (SELECT MAX(id) FROM customers));
SELECT setval(pg_get_serial_sequence('restaurant_tables', 'id'), (SELECT MAX(id) FROM restaurant_tables));
SELECT setval(pg_get_serial_sequence('reviews', 'id'), (SELECT MAX(id) FROM reviews));
