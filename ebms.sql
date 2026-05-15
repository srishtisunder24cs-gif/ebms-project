CREATE TABLE consumer (
    consumer_id INT PRIMARY KEY AUTO_INCREMENT,
    full_name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(15),
    address TEXT,
    meter_number VARCHAR(50),
    password VARCHAR(100)
);

CREATE TABLE admin (
    admin_id INT PRIMARY KEY AUTO_INCREMENT,
    admin_name VARCHAR(100),
    email VARCHAR(100),
    password VARCHAR(100)
);

CREATE TABLE bill (
    bill_id INT PRIMARY KEY AUTO_INCREMENT,
    consumer_id INT,
    month VARCHAR(20),
    units_consumed INT,
    total_amount DECIMAL(10,2),
    bill_status VARCHAR(20),
    FOREIGN KEY (consumer_id) REFERENCES consumer(consumer_id)
);

CREATE TABLE complaint (
    complaint_id INT PRIMARY KEY AUTO_INCREMENT,
    consumer_id INT,
    subject VARCHAR(255),
    description TEXT,
    complaint_status VARCHAR(20),
    FOREIGN KEY (consumer_id) REFERENCES consumer(consumer_id)
);