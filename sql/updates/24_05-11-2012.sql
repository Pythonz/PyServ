ALTER TABLE `users` ADD COLUMN id bigint(20) not null auto_increment key FIRST;
DROP TABLE IF EXISTS `statistics`;
CREATE TABLE IF NOT EXISTS `statistics` (`attribute` varchar(256) not null key, `value` text);
INSERT INTO `statistics` (attribute, `value`) VALUES ('kicks', '0'),('kills', '0');
