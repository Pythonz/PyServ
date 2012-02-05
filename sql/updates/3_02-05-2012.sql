RENAME TABLE `chanlist` TO `channelinfo`;
ALTER TABLE `channelinfo` ADD COLUMN (modes text, flags text);
UPDATE `channelinfo` SET modes = '';
UPDATE `channelinfo` SET flags = '';
