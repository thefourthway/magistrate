-- ver: 1
-- backwards_compatible: false
-- up
CREATE TABLE abc(
    id BIGSERIAL PRIMARY KEY,
    version INTEGER
);
CREATE TYPE status ('on', 'off', 'pending');
