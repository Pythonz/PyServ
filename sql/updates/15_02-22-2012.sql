ALTER TABLE `users` ADD COLUMN flags text;
UPDATE `users` SET `flags` = 'n';
