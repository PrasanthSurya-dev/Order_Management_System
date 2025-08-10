PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE admin (
            id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL, password TEXT NOT NULL);
INSERT INTO admin VALUES(1,'admin','adminpass');
CREATE TABLE customers (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    username TEXT UNIQUE NOT NULL,

    password TEXT NOT NULL,

    name TEXT,

    address TEXT,

    contact TEXT

);
INSERT INTO customers VALUES(1,'customer1','pass1','Surya Prasanth','Vizag','9876543210');
INSERT INTO customers VALUES(2,'sai','pass2','Sai Kumar','Vijayawada','8765432109');
INSERT INTO customers VALUES(3,'ajay','pass3','Ajay Varma','Hyderabad','9988776655');
INSERT INTO customers VALUES(4,'pavan','pass4','Pavan Teja','Guntur','8877665544');
INSERT INTO customers VALUES(5,'rajesh','pass5','Rajesh Reddy','Nellore','7766554433');
INSERT INTO customers VALUES(6,'kiran','pass6','Kiran Kumar','Ongole','6655443322');
INSERT INTO customers VALUES(7,'vamsi','pass7','Vamsi Krishna','Warangal','5544332211');
INSERT INTO customers VALUES(8,'ravi','pass8','Ravi Teja','Karimnagar','4433221100');
INSERT INTO customers VALUES(9,'mahesh','pass9','Mahesh Babu','Kurnool','3322110099');
INSERT INTO customers VALUES(10,'praveen','pass10','Praveen Kumar','Kadapa','2211009988');
INSERT INTO customers VALUES(11,'suresh','pass11','Suresh Reddy','Tirupati','1100998877');
INSERT INTO customers VALUES(12,'lokesh','pass12','Lokesh Varma','Anantapur','0099887766');
INSERT INTO customers VALUES(13,'anil','pass13','Anil Kumar','Chittoor','9988776655');
INSERT INTO customers VALUES(14,'srinivas','pass14','Srinivas Rao','Nizamabad','8877665544');
INSERT INTO customers VALUES(15,'ram','pass15','Ram Mohan','Adilabad','7766554433');
INSERT INTO customers VALUES(16,'manoj','pass16','Manoj Kumar','Srikakulam','6655443322');
INSERT INTO customers VALUES(17,'deepak','pass17','Deepak Reddy','Rajahmundry','5544332211');
INSERT INTO customers VALUES(18,'arun','pass18','Arun Teja','Kakinada','4433221100');
INSERT INTO customers VALUES(19,'bharath','pass19','Bharath Kumar','Vizianagaram','3322110099');
INSERT INTO customers VALUES(20,'dinesh','pass20','Dinesh Babu','Machilipatnam','2211009988');
INSERT INTO customers VALUES(22,'ramesh','pass22','Ramesh','Hyderabad','7367829873');
INSERT INTO customers VALUES(23,'kumar','kumar','Kumar ','Kakinada','6785275926');
INSERT INTO customers VALUES(24,'rahul reddy','rahul','Rahul Reddy','Mumbai','9568285628');
INSERT INTO customers VALUES(25,'vikram','vikram123','Vikram','East Godavari','6445825479');
INSERT INTO customers VALUES(26,'kaushal','pass25','Kaushal','Madhuravada, Vizag','6573846572');
CREATE TABLE products (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT,

    description TEXT,

    price REAL,

    stock INTEGER

, image_url TEXT);
INSERT INTO products VALUES(1,'Wireless Earbuds','High-quality wireless earbuds',2500.0,200,'https://images.pexels.com/photos/3394650/pexels-photo-3394650.jpeg');
INSERT INTO products VALUES(2,'Bluetooth Speaker','Portable bluetooth speaker',1800.0,1,'https://images.pexels.com/photos/1649771/pexels-photo-1649771.jpeg');
INSERT INTO products VALUES(3,'Smart Watch','Fitness and notification smart watch',4000.0,147,'https://images.pexels.com/photos/437037/pexels-photo-437037.jpeg');
INSERT INTO products VALUES(4,'LED Desk Lamp','Stylish LED desk lamp',1200.0,299,'https://images.pexels.com/photos/1112598/pexels-photo-1112598.jpeg');
INSERT INTO products VALUES(5,'USB-C Power Bank','Fast charging USB-C power bank',2200.0,399,'https://images.pexels.com/photos/4219654/pexels-photo-4219654.jpeg');
INSERT INTO products VALUES(6,'Portable SSD','High-speed portable SSD storage',4500.0,49,'https://images.pexels.com/photos/2582937/pexels-photo-2582937.jpeg');
INSERT INTO products VALUES(7,'Noise Cancelling Headphones','Over-ear noise cancelling headphones',6500.0,359,'https://images.pexels.com/photos/3394651/pexels-photo-3394651.jpeg');
INSERT INTO products VALUES(8,'Gaming Mouse','RGB gaming mouse with high DPI',1600.0,474,'https://images.pexels.com/photos/2115256/pexels-photo-2115256.jpeg');
INSERT INTO products VALUES(9,'Wireless Keyboard','Slim wireless keyboard',2400.0,412,'https://images.pexels.com/photos/2047905/pexels-photo-2047905.jpeg');
INSERT INTO products VALUES(10,'Smart Home Plug','WiFi-enabled smart plug',1300.0,0,'https://t3.ftcdn.net/jpg/15/34/90/14/240_F_1534901445_qBs8EvbGvzwJYUsEv3jP1dwrHMU8P6qU.jpg');
INSERT INTO products VALUES(12,'Samsung S25 Ultra','The ultimate flagship experience with a pro-grade camera system, brilliant Dynamic AMOLED display, and next-generation AI-powered performance.',124999.0,148,'https://images.pexels.com/photos/30466740/pexels-photo-30466740.jpeg');
INSERT INTO products VALUES(13,'iPhone 16 Pro Max','Experience the future with the A19 Pro chip, a revolutionary triple-camera system, and a stunning ProMotion XDR display. Crafted from aerospace-grade titanium.',189999.0,244,'https://images.pexels.com/photos/29020349/pexels-photo-29020349.jpeg');
CREATE TABLE orders (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    customer_id INTEGER,

    items TEXT,             -- JSON string: {"1":2,"3":1}

    total REAL,

    payment_method TEXT,

    delivery_date TEXT,

    status TEXT DEFAULT 'Order Received', cancellation_timestamp TEXT, order_date TEXT, actual_delivery_date TEXT, cancellation_refund TEXT,

    FOREIGN KEY (customer_id) REFERENCES customers(id)

);
INSERT INTO orders VALUES(1,1,'{"1":2,"3":1}',9000.0,'Cash On Delivery','2025-07-15','Delivered',NULL,'2025-07-12',NULL,NULL);
INSERT INTO orders VALUES(2,2,'{"2":1}',1800.0,'Online Payment','2025-07-12','Delivered',NULL,'2025-07-09',NULL,NULL);
INSERT INTO orders VALUES(3,3,'{"4":1,"5":2}',5600.0,'Cash On Delivery','2025-07-14','Delivered',NULL,'2025-07-11',NULL,NULL);
INSERT INTO orders VALUES(4,4,'{"6":1}',4500.0,'Online Payment','2025-07-17','Delivered',NULL,'2025-07-14',NULL,NULL);
INSERT INTO orders VALUES(5,5,'{"7":2}',13000.0,'Cash On Delivery','2025-07-19','Delivered',NULL,'2025-07-16',NULL,NULL);
INSERT INTO orders VALUES(6,6,'{"8":2,"9":1}',5600.0,'Online Payment','2025-07-20','Delivered',NULL,'2025-07-17',NULL,NULL);
INSERT INTO orders VALUES(7,7,'{"10":1}',1300.0,'Cash On Delivery','2025-07-16','Delivered',NULL,'2025-07-13',NULL,NULL);
INSERT INTO orders VALUES(8,8,'{"1":1,"3":1}',6500.0,'Online Payment','2025-07-13','Delivered',NULL,'2025-07-10',NULL,NULL);
INSERT INTO orders VALUES(9,9,'{"5":1}',2200.0,'Cash On Delivery','2025-07-18','Delivered',NULL,'2025-07-15',NULL,NULL);
INSERT INTO orders VALUES(10,10,'{"6":1,"2":1}',6300.0,'Online Payment','2025-07-21','Delivered',NULL,'2025-07-18',NULL,NULL);
INSERT INTO orders VALUES(11,1,'{"1": 3}',7500.0,'UPI','2025-07-31','Delivered',NULL,'2025-07-28',NULL,NULL);
INSERT INTO orders VALUES(12,1,'{"1": 2}',5000.0,'UPI','2025-07-31','Delivered',NULL,'2025-07-28',NULL,NULL);
INSERT INTO orders VALUES(13,1,'{"3": 1}',4000.0,'Debit Card','2025-07-29','Delivered',NULL,'2025-07-26',NULL,NULL);
INSERT INTO orders VALUES(14,3,'{"4": 1}',1200.0,'Credit Card','2025-07-29','Delivered',NULL,'2025-07-26',NULL,NULL);
INSERT INTO orders VALUES(15,3,'{"3": 1}',4000.0,'Debit Card','2025-07-29','Delivered',NULL,'2025-07-26',NULL,NULL);
INSERT INTO orders VALUES(16,12,'{"6": 2}',9000.0,'UPI','2025-07-29','Delivered',NULL,'2025-07-26',NULL,NULL);
INSERT INTO orders VALUES(17,3,'{"9": 3}',7200.0,'Cash on Delivery','2025-07-30','Delivered',NULL,'2025-07-27',NULL,NULL);
INSERT INTO orders VALUES(18,1,'{"1": 2}',5000.0,'Cash on Delivery','2025-08-05','Delivered',NULL,'2025-08-02',NULL,NULL);
INSERT INTO orders VALUES(19,1,'{"8": 1}',1600.0,'Debit Card','2025-08-05','Delivered',NULL,'2025-08-02',NULL,NULL);
INSERT INTO orders VALUES(20,1,'{"12": 1}',124999.0,'Credit Card','2025-08-07','Delivered',NULL,'2025-08-04',NULL,NULL);
INSERT INTO orders VALUES(21,5,'{"12": 1}',124999.0,'UPI','2025-08-07','Delivered',NULL,'2025-08-04','2025-08-05',NULL);
INSERT INTO orders VALUES(22,8,'{"3": 1}',4000.0,'Cash on Delivery','2025-08-09','Delivered',NULL,'2025-08-05','2025-08-05',NULL);
INSERT INTO orders VALUES(23,14,'{"5": 1}',2200.0,'UPI','2025-08-09','Delivered',NULL,'2025-08-05','2025-08-06',NULL);
INSERT INTO orders VALUES(24,24,'{"7": 1, "8": 1}',8100.0,'Cash on Delivery','2025-08-09','Cancelled','2025-08-05T22:20:30.388280','2025-08-05',NULL,NULL);
INSERT INTO orders VALUES(25,24,'{"1": 1}',2500.0,'UPI','2025-08-09','Cancelled','2025-08-05T22:31:35.980604','2025-08-05',NULL,'Refund initiated successfully to your account.');
INSERT INTO orders VALUES(26,1,'{"4": 1}',1200.0,'Cash on Delivery','2025-08-09','Cancelled','2025-08-05T22:44:41.250734','2025-08-05',NULL,NULL);
INSERT INTO orders VALUES(27,6,'{"9": 1}',2400.0,'Credit Card','2025-08-09','Cancelled','2025-08-05T23:06:05.564839','2025-08-05',NULL,NULL);
INSERT INTO orders VALUES(28,6,'{"6": 1}',4500.0,'Credit Card','2025-08-09','Cancelled','2025-08-05T23:50:13.896947','2025-08-05',NULL,NULL);
INSERT INTO orders VALUES(29,17,'{"5": 1}',2200.0,'Cash on Delivery','2025-08-09','Cancelled','2025-08-05T23:12:24.032297','2025-08-05',NULL,NULL);
INSERT INTO orders VALUES(30,26,'{"12": 1}',124999.0,'Cash on Delivery','2025-08-10','Cancelled','2025-08-07T23:51:25.310821','2025-08-06',NULL,'');
INSERT INTO orders VALUES(31,24,'{"4": 1}',1200.0,'Cash on Delivery','2025-08-10','Cancelled','2025-08-06T22:35:29.304311','2025-08-06',NULL,'');
INSERT INTO orders VALUES(32,3,'{"5": 1}',2200.0,'UPI','2025-08-10','Cancelled','2025-08-06T22:40:56.607410','2025-08-06',NULL,'Refund initiated successfully to your account.');
INSERT INTO orders VALUES(33,17,'{"4": 1}',1200.0,'Debit Card','2025-08-10','Cancelled','2025-08-06T23:21:22.828540','2025-08-06',NULL,'Refund initiated successfully to your account.');
INSERT INTO orders VALUES(34,22,'{"8": 1}',1600.0,'Credit Card','2025-08-11','Cancelled','2025-08-07T22:57:41.453664','2025-08-07',NULL,'Refund initiated successfully to your account.');
INSERT INTO sqlite_sequence VALUES('customers',26);
INSERT INTO sqlite_sequence VALUES('products',13);
INSERT INTO sqlite_sequence VALUES('orders',34);
CREATE VIEW orders_view AS

SELECT 

    o.id AS order_id,

    c.name AS customer_name,

    o.items,

    o.total,

    o.payment_method,

    o.delivery_date,

    o.status

FROM orders o

JOIN customers c ON o.customer_id = c.id;
COMMIT;
