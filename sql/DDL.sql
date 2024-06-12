CREATE DATABASE "ArtKomplect"
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False 
    LC_COLLATE='ru_RU.utf8' 
    LC_CTYPE='ru_RU.utf8';

\c ArtKomplect;

CREATE TABLE IF NOT EXISTS images(
    id  SERIAL PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    file_id VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS addresses(    
    id SERIAL PRIMARY KEY,
    user_id DOUBLE PRECISION NOT NULL,
    index VARCHAR(6), 
    country VARCHAR(255),
    city VARCHAR(255), 
    street VARCHAR(255),
    house VARCHAR(255),
    building VARCHAR(255),
    office VARCHAR(255),
    visible BOOLEAN
);

CREATE TABLE IF NOT EXISTS items(
    id VARCHAR(255) PRIMARY KEY,
    group_name VARCHAR(255),
    name VARCHAR(500),
    description VARCHAR(1000),
    manufacturer_name VARCHAR(255) ,
    image VARCHAR(255),
    price_per_unit NUMERIC,
    units VARCHAR(255),
    currency VARCHAR(3),
    avaible INTEGER,
    visible BOOLEAN
);
CREATE Table IF NOT EXISTS carts(
    user_id DOUBLE PRECISION,
    item_id VARCHAR(255) REFERENCES items(id), 
    amount INTEGER
);
ALTER TABLE carts ADD CONSTRAINT CartItemsUnique UNIQUE(user_id, item_id);

CREATE TABLE IF NOT EXISTS orders (
    id VARCHAR(25) PRIMARY KEY,
    user_id DOUBLE PRECISION,
    address_id INTEGER REFERENCES addresses(id),
    total_sum NUMERIC,
    payment_method VARCHAR(50),
    status VARCHAR(50),
    payment_status VARCHAR(50),
    creating_time TIMESTAMP,
    is_takeaway integer
);
ALTER TABLE orders ADD CONSTRAINT is_takeaway check (is_takeaway >=0 and is_takeaway <=2);
CREATE TABLE IF NOT EXISTS ordered_items(
    item_id VARCHAR(255) REFERENCES items(id),
    order_id Varchar(25) REFERENCES orders(id),
    amount INTEGER
);
ALTER TABLE ordered_items ADD CONSTRAINT OrderedItemsUnique UNIQUE(item_id, order_id);
