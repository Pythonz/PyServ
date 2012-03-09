RENAME TABLE `bots` TO `gateway`;
DROP TABLE IF EXISTS `statistics`;
CREATE TABLE IF NOT EXISTS `statistics` (kicks int(100), kills int(100));
INSERT INTO `statistics` (kicks, kills) VALUES (0, 0);
