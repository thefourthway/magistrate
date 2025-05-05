-- ver: 1
-- up
CREATE TABLE abc (id serial primary key, val integer);
INSERT INTO abc (val) VALUES (22);

-- down
DROP TABLE abc;
