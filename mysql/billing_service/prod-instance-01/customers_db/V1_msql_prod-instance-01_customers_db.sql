-- Release Query
ALTER TABLE users ADD COLUMN email VARCHAR(255);

-- Rollback Query
ALTER TABLE users DROP COLUMN email;