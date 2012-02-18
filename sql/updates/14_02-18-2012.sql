ALTER TABLE `channelinfo` ADD COLUMN spamscan text;
UPDATE `channelinfo` SET `spamscan` = '10:5';
