--We are up to date

-- Not!

ALTER TABLE `smoon`.`host` ADD COLUMN `pub_uuid` VARCHAR(40)  NOT NULL AFTER `u_u_id`;

CREATE OR REPLACE VIEW `SELINUX_ENABLED` AS select `host`.`selinux_enabled` AS `enabled`,count(`host`.`selinux_enabled`) AS `cnt` from `host` group by `host`.`selinux_enabled` order by count(`host`.`selinux_enabled`) desc

CREATE OR REPLACE VIEW `SELINUX_ENFORCE` AS select `host`.`selinux_enforce` AS `enforce`,count(`host`.`selinux_enforce`) AS `cnt` from `host` group by `host`.`selinux_enforce` order by count(`host`.`selinux_enforce`) desc


