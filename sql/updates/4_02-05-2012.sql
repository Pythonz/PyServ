ALTER TABLE `channelinfo` ADD COLUMN topic text;
UPDATE `channelinfo` SET topic = '';
