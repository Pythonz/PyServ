ALTER TABLE `users` ADD COLUMN id bigint(20) not null auto_increment key FIRST;
DROP TABLE IF EXISTS `statistics`;
CREATE TABLE IF NOT EXISTS `statistics` (`attribute` text not null key(0), `value` text, primary key (`attribute`));
INSERT INTO `statistics` (attribute, `value`) VALUES ('kicks', '0'),('kills', '0');
