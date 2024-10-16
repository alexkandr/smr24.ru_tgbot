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
    user_id DOUBLE PRECISION,
    index VARCHAR(6), 
    country VARCHAR(255),
    city VARCHAR(255), 
    street VARCHAR(255),
    house VARCHAR(255),
    building VARCHAR(255),
    office VARCHAR(255),
    is_visible BOOLEAN,
    is_takeaway BOOLEAN
);

CREATE Table IF NOT EXISTS groups(
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255),
    parent VARCHAR REFERENCES groups(id),
    level INTEGER
);

CREATE TABLE IF NOT EXISTS items(
    id VARCHAR(255) PRIMARY KEY,
    group_id VARCHAR(255) REFERENCES groups(id),
    name VARCHAR(500),
    description VARCHAR(1000),
    manufacturer_name VARCHAR(255) ,
    image VARCHAR(255),
    price_per_unit NUMERIC,
    units VARCHAR(255),
    currency VARCHAR(3),
    available INTEGER,
    is_visible BOOLEAN,
    has_annotation BOOLEAN,
    annotation VARCHAR(255)
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
    is_takeaway BOOLEAN
);
CREATE TABLE IF NOT EXISTS ordered_items(
    item_id VARCHAR(255) REFERENCES items(id),
    order_id Varchar(25) REFERENCES orders(id),
    amount INTEGER
);
ALTER TABLE ordered_items ADD CONSTRAINT OrderedItemsUnique UNIQUE(item_id, order_id);

create table IF NOT exists users(
user_id  DOUBLE precision,
phone_number  VARCHAR(15),
is_current  BOOLEAN
);

create or replace view main_order_view as select o.id as "id заказа", o.creating_time as "время создания", u.phone_number as "телефон заказчика", a.city || ' '|| a.street ||' '|| a.house || '/'||a.building as "адрес доставки", o.is_takeaway as "самовывоз",  i.id as "id товара", i.name as "название товара", oi.amount as "количество"
from orders o left join ordered_items oi on o.id = oi.order_id
left join items i on oi.item_id = i.id 
left join addresses a on o.address_id =  a.id
left join users u on o.user_id = u.user_id
order by o.creating_time desc;

