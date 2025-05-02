-- ver: 4
-- up
ALTER TABLE abc ADD COLUMN new_column_three INTEGER;
-- down
ALTER TABLE abc DROP COLUMN new_column_three INTEGER;
