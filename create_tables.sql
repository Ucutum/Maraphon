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
    title   STRING NOT NULL
);

CREATE TABLE tasks (
    id          STRING  PRIMARY KEY
                        NOT NULL
                        UNIQUE,
    main        STRING  REFERENCES maraphons (id) 
                        NOT NULL,
    [index]     INTEGER UNIQUE
                        NOT NULL,
    name        STRING  NOT NULL,
    date        STRING  NOT NULL,
    description STRING  NOT NULL
);

CREATE TABLE states (
    task STRING  REFERENCES tasks (id) 
                 NOT NULL,
    user STRING  NOT NULL
                 REFERENCES users (id),
    done BOOLEAN NOT NULL
);
