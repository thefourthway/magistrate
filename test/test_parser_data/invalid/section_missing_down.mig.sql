-- ver: 1
-- up
CREATE TABLE abc(
    id BIGSERIAL PRIMARY KEY,
    version INTEGER
);
CREATE TYPE status ('on', 'off', 'pending');
