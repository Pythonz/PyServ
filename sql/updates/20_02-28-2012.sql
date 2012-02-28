ALTER TABLE `users` ADD COLUMN suspended text;
UPDATE `users` SET `suspended` = '0';
