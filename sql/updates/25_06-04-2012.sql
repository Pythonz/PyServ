SET FOREIGN_KEY_CHECKS=0;
ALTER TABLE `banlist` ADD COLUMN `id`  bigint(20) NOT NULL FIRST ;
ALTER TABLE `banlist` ADD PRIMARY KEY (`id`);
ALTER TABLE `banlist` MODIFY COLUMN `id`  bigint(20) NOT NULL AUTO_INCREMENT FIRST ;
ALTER TABLE `channels` MODIFY COLUMN `flag`  enum('n','q','a','o','h','v','b') CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL AFTER `user`;
ALTER TABLE `ipchan` ADD COLUMN `id`  bigint(20) NOT NULL FIRST ;
ALTER TABLE `ipchan` ADD PRIMARY KEY (`id`);
ALTER TABLE `ipchan` MODIFY COLUMN `id`  bigint(20) NOT NULL AUTO_INCREMENT FIRST ;
ALTER TABLE `memo` ADD COLUMN `id`  bigint(20) NOT NULL FIRST ;
ALTER TABLE `memo` ADD PRIMARY KEY (`id`);
ALTER TABLE `memo` MODIFY COLUMN `id`  bigint(20) NOT NULL AUTO_INCREMENT FIRST ;
ALTER TABLE `suspended` ADD COLUMN `id`  bigint(20) NOT NULL FIRST ;
ALTER TABLE `suspended` ADD PRIMARY KEY (`id`);
ALTER TABLE `suspended` MODIFY COLUMN `id`  bigint(20) NOT NULL AUTO_INCREMENT FIRST ;
ALTER TABLE `trust` ADD COLUMN `id`  bigint(20) NOT NULL FIRST ;
ALTER TABLE `trust` ADD PRIMARY KEY (`id`);
ALTER TABLE `trust` MODIFY COLUMN `id`  bigint(20) NOT NULL AUTO_INCREMENT FIRST ;
DROP TABLE `challenges`;
SET FOREIGN_KEY_CHECKS=1;