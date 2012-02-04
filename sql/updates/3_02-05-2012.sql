RENAME TABLE `chanlist` TO `channelinfo`;
ALTER TABLE `channelinfo` ADD COLUMN (modes text, flags text);
