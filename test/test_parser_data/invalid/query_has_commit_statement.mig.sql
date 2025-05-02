-- ver: 1
-- up

CREATE TABLE abc (
    id SERIAL PRIMARY KEY,
    version INTEGER
);

COMMIT;

-- down
DROP TABLE abc;
