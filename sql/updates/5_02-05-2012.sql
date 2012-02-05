ALTER TABLE `online` ADD COLUMN address text;
CREATE TABLE IF NOT EXIST `trust` (address text, limit int);
