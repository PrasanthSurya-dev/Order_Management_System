-- Drop existing tables and views to ensure a clean start
DROP VIEW IF EXISTS orders_view;
DROP TABLE IF EXISTS returns, orders, products, customers, admin CASCADE;

-- Create all tables with PostgreSQL-specific syntax
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    address TEXT,
    contact VARCHAR(255)
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    description TEXT,
    price DECIMAL(10, 2),
    stock INTEGER,
    image_url TEXT
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    items JSONB,
    total DECIMAL(10, 2),
    payment_method VARCHAR(255),
    delivery_date DATE,
    status VARCHAR(255) DEFAULT 'Order Received',
    cancellation_timestamp TIMESTAMPTZ,
    order_date DATE,
    actual_delivery_date DATE,
    cancellation_refund TEXT
);

CREATE TABLE admin (
    id INTEGER PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

-- Insert admin user
INSERT INTO admin (id, username, password) VALUES (1, 'admin', 'adminpass');

-- Insert customers (using single quotes for strings is standard)
INSERT INTO customers (id, username, password, name, address, contact) VALUES
(1, 'customer1', 'pass1', 'Surya Prasanth', 'Vizag', '9876543210'),
(2, 'sai', 'pass2', 'Sai Kumar', 'Vijayawada', '8765432109'),
(3, 'ajay', 'pass3', 'Ajay Varma', 'Hyderabad', '9988776655'),
(4, 'pavan', 'pass4', 'Pavan Teja', 'Guntur', '8877665544'),
(5, 'rajesh', 'pass5', 'Rajesh Reddy', 'Nellore', '7766554433'),
(6, 'kiran', 'pass6', 'Kiran Kumar', 'Ongole', '6655443322'),
(7, 'vamsi', 'pass7', 'Vamsi Krishna', 'Warangal', '5544332211'),
(8, 'ravi', 'pass8', 'Ravi Teja', 'Karimnagar', '4433221100'),
(9, 'mahesh', 'pass9', 'Mahesh Babu', 'Kurnool', '3322110099'),
(10, 'praveen', 'pass10', 'Praveen Kumar', 'Kadapa', '2211009988'),
(11, 'suresh', 'pass11', 'Suresh Reddy', 'Tirupati', '1100998877'),
(12, 'lokesh', 'pass12', 'Lokesh Varma', 'Anantapur', '0099887766'),
(13, 'anil', 'pass13', 'Anil Kumar', 'Chittoor', '9988776655'),
(14, 'srinivas', 'pass14', 'Srinivas Rao', 'Nizamabad', '8877665544'),
(15, 'ram', 'pass15', 'Ram Mohan', 'Adilabad', '7766554433'),
(16, 'manoj', 'pass16', 'Manoj Kumar', 'Srikakulam', '6655443322'),
(17, 'deepak', 'pass17', 'Deepak Reddy', 'Rajahmundry', '5544332211'),
(18, 'arun', 'pass18', 'Arun Teja', 'Kakinada', '4433221100'),
(19, 'bharath', 'pass19', 'Bharath Kumar', 'Vizianagaram', '3322110099'),
(20, 'dinesh', 'pass20', 'Dinesh Babu', 'Machilipatnam', '2211009988'),
(22, 'ramesh', 'pass22', 'Ramesh', 'Hyderabad', '7367829873'),
(23, 'kumar', 'kumar', 'Kumar ', 'Kakinada', '6785275926'),
(24, 'rahul reddy', 'rahul', 'Rahul Reddy', 'Mumbai', '9568285628'),
(25, 'vikram', 'vikram123', 'Vikram', 'East Godavari', '6445825479'),
(26, 'kaushal', 'pass25', 'Kaushal', 'Madhuravada, Vizag', '6573846572');

-- Insert products
INSERT INTO products (id, name, description, price, stock, image_url) VALUES
(1, 'Wireless Earbuds', 'High-quality wireless earbuds', 2500.00, 200, 'https://images.pexels.com/photos/3394650/pexels-photo-3394650.jpeg'),
(2, 'Bluetooth Speaker', 'Portable bluetooth speaker', 1800.00, 1, 'https://images.pexels.com/photos/1649771/pexels-photo-1649771.jpeg'),
(3, 'Smart Watch', 'Fitness and notification smart watch', 4000.00, 147, 'https://images.pexels.com/photos/437037/pexels-photo-437037.jpeg'),
(4, 'LED Desk Lamp', 'Stylish LED desk lamp', 1200.00, 299, 'https://images.pexels.com/photos/1112598/pexels-photo-1112598.jpeg'),
(5, 'USB-C Power Bank', 'Fast charging USB-C power bank', 2200.00, 399, 'https://images.pexels.com/photos/4219654/pexels-photo-4219654.jpeg'),
(6, 'Portable SSD', 'High-speed portable SSD storage', 4500.00, 49, 'https://images.pexels.com/photos/2582937/pexels-photo-2582937.jpeg'),
(7, 'Noise Cancelling Headphones', 'Over-ear noise cancelling headphones', 6500.00, 359, 'https://images.pexels.com/photos/3394651/pexels-photo-3394651.jpeg'),
(8, 'Gaming Mouse', 'RGB gaming mouse with high DPI', 1600.00, 474, 'https://images.pexels.com/photos/2115256/pexels-photo-2115256.jpeg'),
(9, 'Wireless Keyboard', 'Slim wireless keyboard', 2400.00, 412, 'https://images.pexels.com/photos/2047905/pexels-photo-2047905.jpeg'),
(10, 'Smart Home Plug', 'WiFi-enabled smart plug', 1300.00, 0, 'https://t3.ftcdn.net/jpg/15/34/90/14/240_F_1534901445_qBs8EvbGvzwJYUsEv3jP1dwrHMU8P6qU.jpg'),
(12, 'Samsung S25 Ultra', 'The ultimate flagship experience...', 124999.00, 148, 'https://images.pexels.com/photos/30466740/pexels-photo-30466740.jpeg'),
(13, 'iPhone 16 Pro Max', 'Experience the future with the A19 Pro chip...', 189999.00, 244, 'https://images.pexels.com/photos/29020349/pexels-photo-29020349.jpeg');

-- Insert orders (using single quotes for strings and correct date/timestamp formats)
INSERT INTO orders (id, customer_id, items, total, payment_method, delivery_date, status, cancellation_timestamp, order_date, actual_delivery_date, cancellation_refund) VALUES
(1, 1, '{"1":2,"3":1}', 9000.00, 'Cash On Delivery', '2025-07-15', 'Delivered', NULL, '2025-07-12', NULL, NULL),
(2, 2, '{"2":1}', 1800.00, 'Online Payment', '2025-07-12', 'Delivered', NULL, '2025-07-09', NULL, NULL),
(3, 3, '{"4":1,"5":2}', 5600.00, 'Cash On Delivery', '2025-07-14', 'Delivered', NULL, '2025-07-11', NULL, NULL),
(4, 4, '{"6":1}', 4500.00, 'Online Payment', '2025-07-17', 'Delivered', NULL, '2025-07-14', NULL, NULL),
(5, 5, '{"7":2}', 13000.00, 'Cash On Delivery', '2025-07-19', 'Delivered', NULL, '2025-07-16', NULL, NULL),
(6, 6, '{"8":2,"9":1}', 5600.00, 'Online Payment', '2025-07-20', 'Delivered', NULL, '2025-07-17', NULL, NULL),
(7, 7, '{"10":1}', 1300.00, 'Cash On Delivery', '2025-07-16', 'Delivered', NULL, '2025-07-13', NULL, NULL),
(8, 8, '{"1":1,"3":1}', 6500.00, 'Online Payment', '2025-07-13', 'Delivered', NULL, '2025-07-10', NULL, NULL),
(9, 9, '{"5":1}', 2200.00, 'Cash On Delivery', '2025-07-18', 'Delivered', NULL, '2025-07-15', NULL, NULL),
(10, 10, '{"6":1,"2":1}', 6300.00, 'Online Payment', '2025-07-21', 'Delivered', NULL, '2025-07-18', NULL, NULL),
(11, 1, '{"1": 3}', 7500.00, 'UPI', '2025-07-31', 'Delivered', NULL, '2025-07-28', NULL, NULL),
(12, 1, '{"1": 2}', 5000.00, 'UPI', '2025-07-31', 'Delivered', NULL, '2025-07-28', NULL, NULL),
(13, 1, '{"3": 1}', 4000.00, 'Debit Card', '2025-07-29', 'Delivered', NULL, '2025-07-26', NULL, NULL),
(14, 3, '{"4": 1}', 1200.00, 'Credit Card', '2025-07-29', 'Delivered', NULL, '2025-07-26', NULL, NULL),
(15, 3, '{"3": 1}', 4000.00, 'Debit Card', '2025-07-29', 'Delivered', NULL, '2025-07-26', NULL, NULL),
(16, 12, '{"6": 2}', 9000.00, 'UPI', '2025-07-29', 'Delivered', NULL, '2025-07-26', NULL, NULL),
(17, 3, '{"9": 3}', 7200.00, 'Cash on Delivery', '2025-07-30', 'Delivered', NULL, '2025-07-27', NULL, NULL),
(18, 1, '{"1": 2}', 5000.00, 'Cash on Delivery', '2025-08-05', 'Delivered', NULL, '2025-08-02', NULL, NULL),
(19, 1, '{"8": 1}', 1600.00, 'Debit Card', '2025-08-05', 'Delivered', NULL, '2025-08-02', NULL, NULL),
(20, 1, '{"12": 1}', 124999.00, 'Credit Card', '2025-08-07', 'Delivered', NULL, '2025-08-04', NULL, NULL),
(21, 5, '{"12": 1}', 124999.00, 'UPI', '2025-08-07', 'Delivered', NULL, '2025-08-04', '2025-08-05', NULL),
(22, 8, '{"3": 1}', 4000.00, 'Cash on Delivery', '2025-08-09', 'Delivered', NULL, '2025-08-05', '2025-08-05', NULL),
(23, 14, '{"5": 1}', 2200.00, 'UPI', '2025-08-09', 'Delivered', NULL, '2025-08-05', '2025-08-06', NULL),
(24, 24, '{"7": 1, "8": 1}', 8100.00, 'Cash on Delivery', '2025-08-09', 'Cancelled', '2025-08-05 22:20:30.388280+00', '2025-08-05', NULL, NULL),
(25, 24, '{"1": 1}', 2500.00, 'UPI', '2025-08-09', 'Cancelled', '2025-08-05 22:31:35.980604+00', '2025-08-05', NULL, 'Refund initiated successfully to your account.'),
(26, 1, '{"4": 1}', 1200.00, 'Cash on Delivery', '2025-08-09', 'Cancelled', '2025-08-05 22:44:41.250734+00', '2025-08-05', NULL, NULL),
(27, 6, '{"9": 1}', 2400.00, 'Credit Card', '2025-08-09', 'Cancelled', '2025-08-05 23:06:05.564839+00', '2025-08-05', NULL, NULL),
(28, 6, '{"6": 1}', 4500.00, 'Credit Card', '2025-08-09', 'Cancelled', '2025-08-05 23:50:13.896947+00', '2025-08-05', NULL, NULL),
(29, 17, '{"5": 1}', 2200.00, 'Cash on Delivery', '2025-08-09', 'Cancelled', '2025-08-05 23:12:24.032297+00', '2025-08-05', NULL, NULL),
(30, 26, '{"12": 1}', 124999.00, 'Cash on Delivery', '2025-08-10', 'Cancelled', '2025-08-07 23:51:25.310821+00', '2025-08-06', NULL, ''),
(31, 24, '{"4": 1}', 1200.00, 'Cash on Delivery', '2025-08-10', 'Cancelled', '2025-08-06 22:35:29.304311+00', '2025-08-06', NULL, ''),
(32, 3, '{"5": 1}', 2200.00, 'UPI', '2025-08-10', 'Cancelled', '2025-08-06 22:40:56.607410+00', '2025-08-06', NULL, 'Refund initiated successfully to your account.'),
(33, 17, '{"4": 1}', 1200.00, 'Debit Card', '2025-08-10', 'Cancelled', '2025-08-06 23:21:22.828540+00', '2025-08-06', NULL, 'Refund initiated successfully to your account.'),
(34, 22, '{"8": 1}', 1600.00, 'Credit Card', '2025-08-11', 'Cancelled', '2025-08-07 22:57:41.453664+00', '2025-08-07', NULL, 'Refund initiated successfully to your account.');

-- After running manual inserts in PostgreSQL, you must update the sequences
-- so the next auto-generated ID is correct.
SELECT setval('customers_id_seq', (SELECT MAX(id) FROM customers));
SELECT setval('products_id_seq', (SELECT MAX(id) FROM products));
SELECT setval('orders_id_seq', (SELECT MAX(id) FROM orders));