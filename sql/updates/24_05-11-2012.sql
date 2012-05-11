ALTER TABLE `users` ADD COLUMN id bigint(20) FIRST;
ALTER TABLE `users` MODIFY COLUMN (id bigint(20) not null auto_increment);
ALTER TABLE `users` ADD PRIMARY KEY (id);
DROP TABLE IF EXISTS `statistics`;
CREATE TABLE IF NOT EXISTS `statistics` (`attribute` text not null, `value` text, primary key (`attribute`));
INSERT INTO `statistics` (attribute, `value`) VALUES ('kicks', '0'),('kills', '0');
