-- ver: 1
-- backwards_compatible: true
-- down
DROP TYPE status;
DROP TABLE abc;
-- up
CREATE TABLE abc(
    id BIGSERIAL PRIMARY KEY,
    version INTEGER
);
CREATE TYPE status ('on', 'off', 'pending');
