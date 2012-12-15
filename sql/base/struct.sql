DROP TABLE IF EXISTS `users`;
CREATE TABLE IF NOT EXISTS `users` (
	`id` bigint(20) not null auto_increment key,
	`name` text,
	`pass` text,
	`email` text,
	`flags` text,
	`modes` text,
	`suspended` text
);

DROP TABLE IF EXISTS `channels`;
CREATE TABLE IF NOT EXISTS `channels` (
	`channel` text,
	`user` text,
	`flag` enum('n', 'q', 'a', 'o', 'h', 'v', 'b')
);

DROP TABLE IF EXISTS `channelinfo`;
CREATE TABLE IF NOT EXISTS `channelinfo` (
	`name` text,
	`modes` text,
	`flags` text,
	`topic` text,
	`welcome` text,
	`spamscan` text,
	`fantasy` text
);

DROP TABLE IF EXISTS `vhosts`;
CREATE TABLE IF NOT EXISTS `vhosts` (
	`user` text,
	`vhost` text,
	`active` text
);

DROP TABLE IF EXISTS `temp_nick`;
CREATE TABLE IF NOT EXISTS `temp_nick` (
	`nick` text,
	`user` text
);

DROP TABLE IF EXISTS `opers`;
CREATE TABLE IF NOT EXISTS `opers` (
	`uid` text
);

DROP TABLE IF EXISTS `feedback`;
CREATE TABLE IF NOT EXISTS `feedback` (
	`user` text,
	`text` text
);

DROP TABLE IF EXISTS `online`;
CREATE TABLE IF NOT EXISTS `online` (
	`uid` text,
	`nick` text,
	`address` text,
	`host` text,
	`username` text
);

DROP TABLE IF EXISTS `trust`;
CREATE TABLE IF NOT EXISTS `trust` (
	`id` bigint(20) not null auto_increment key,
	`address` text,
	`limit` text
);

DROP TABLE IF EXISTS `chanlist`;
CREATE TABLE IF NOT EXISTS `chanlist` (
	`uid` text,
	`channel` text
);

DROP TABLE IF EXISTS `memo`;
CREATE TABLE IF NOT EXISTS `memo` (
	`id` bigint(20) not null auto_increment key,
	`user` text,
	`source` text,
	`message` text
);

DROP TABLE IF EXISTS `banlist`;
CREATE TABLE IF NOT EXISTS `banlist` (
	`id` bigint(20) not null auto_increment key,
	`channel` text,
	`ban` text
);

DROP TABLE IF EXISTS `suspended`;
CREATE TABLE IF NOT EXISTS `suspended` (
	`id` bigint(20) not null auto_increment key,
	`channel` text,
	`reason` text
);

DROP TABLE IF EXISTS `ipchan`;
CREATE TABLE IF NOT EXISTS `ipchan` (
	`id` bigint(20) not null auto_increment key,
	`ip` text,
	`channel` text
);

DROP TABLE IF EXISTS `gateway`;
CREATE TABLE IF NOT EXISTS `gateway` (
	`uid` text
);

DROP TABLE IF EXISTS `glines`;
CREATE TABLE IF NOT EXISTS `glines` (
	`id` bigint(20) not null auto_increment key,
	`mask` text
);

DROP TABLE IF EXISTS `statistics`;
CREATE TABLE IF NOT EXISTS `statistics` (
	`attribute` varchar(256) not null key,
	`value` text
);

INSERT INTO `statistics` (`attribute`, `value`) VALUES ('kicks', '0'),('kills', '0');
