PRAGMA foreign_keys=off;

DROP TABLE IF EXISTS favorites;
DROP TABLE IF EXISTS user;


CREATE TABLE user (
    email       VARCHAR(50) not null PRIMARY KEY,
    password    VARCHAR(50) not null,
    fname       VARCHAR(50) not null,
    lname       VARCHAR(50) not null
);


CREATE TABLE favorites (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    email   VARCHAR(50) not null,
    src     VARCHAR(255),
    title   VARCHAR(255),
    date    VARCHAR(255),

    FOREIGN KEY (email) REFERENCES user(email)
);

PRAGMA foreign_keys=on;
