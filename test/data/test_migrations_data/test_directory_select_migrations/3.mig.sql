-- ver: 3
-- up
ALTER TABLE abc ADD COLUMN new_column_two INTEGER;

-- down
ALTER TABLE abc DROP COLUMN new_column_two INTEGER;
