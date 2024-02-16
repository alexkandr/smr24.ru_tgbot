REATE DATABASE "ArtComplect"
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False 
    LC_COLLATE='ru_RU.utf8' 
    LC_CTYPE='ru_RU.utf8';

CREATE TABLE IF NOT EXISTS images(
    id  SERIAL PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    file_id VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS addresses(    
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    index VARCHAR(6), 
    country VARCHAR(255),
    city VARCHAR(255), 
    street VARCHAR(255),
    house VARCHAR(255),
    building VARCHAR(255),
    office VARCHAR(255)
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
    avaible INTEGER
);
CREATE Table IF NOT EXISTS carts(
    user_id INTEGER,
    item_id VARCHAR(255) REFERENCES items(id), 
    amount INTEGER
);
ALTER TABLE carts ADD CONSTRAINT CartItemsUnique UNIQUE(user_id, item_id);
