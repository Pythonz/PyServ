ALTER TABLE `users` ADD COLUMN modes text;
UPDATE `users` SET `modes` = '+i';
