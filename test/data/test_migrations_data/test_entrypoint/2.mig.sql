-- ver: 2
-- up
ALTER TABLE abc ADD COLUMN email TEXT;
-- down
ALTER TABLE abc DROP COLUMN email;