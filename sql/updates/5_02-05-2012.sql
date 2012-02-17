ALTER TABLE `online` ADD COLUMN address text;
CREATE TABLE IF NOT EXISTS `trust` (address text, `limit` text);
