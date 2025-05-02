-- ver: 1
-- up
CREATE TABLE abc (
    id serial primary key,
    version integer
);
CREATE TYPE status AS enum ('pending', 'approved', 'rejected');
-- down
DROP TYPE status;
DROP TABLE abc;