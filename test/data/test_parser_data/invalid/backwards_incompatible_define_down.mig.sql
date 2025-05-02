-- ver: 2
-- backwards_compatible: false
-- up
CREATE TABLE abc(
    id BIGSERIAL PRIMARY KEY,
    version INTEGER
);
CREATE TYPE status ('on', 'off', 'pending');
-- down
DROP TYPE status;
DROP TABLE abc;