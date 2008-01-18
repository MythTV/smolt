--We are up to date

-- Not!

ALTER TABLE `smoon`.`host` ADD COLUMN `pub_uuid` VARCHAR(40)  NOT NULL AFTER `u_u_id`;

