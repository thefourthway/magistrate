-- ver: 2
-- up
ALTER TABLE abc ADD COLUMN new_column_one INTEGER;

-- down

ALTER TABLE abc DROP COLUMN new_column_one;