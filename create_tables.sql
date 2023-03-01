CREATE TABLE users (
    id   STRING PRIMARY KEY
                UNIQUE
                NOT NULL,
    name STRING NOT NULL
                UNIQUE,
    password STRING NOT NULL
);

CREATE TABLE maraphons (
    id      STRING PRIMARY KEY
                   UNIQUE
                   NOT NULL,
    creator STRING REFERENCES users (id) 
                   NOT NULL,
    name    STRING NOT NULL
);