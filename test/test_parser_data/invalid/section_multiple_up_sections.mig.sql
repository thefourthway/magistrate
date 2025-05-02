-- ver: 1
-- up
CREATE TABLE abc(
    id BIGSERIAL PRIMARY KEY,
    version INTEGER
);
-- up
CREATE TYPE status ('on', 'off', 'pending');
-- down
DROP TYPE status;
DROP TABLE abc;