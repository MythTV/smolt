--We are up to date

-- Not!

ALTER TABLE `host` ADD COLUMN `pub_uuid` VARCHAR(40)  NOT NULL AFTER `u_u_id`;

CREATE OR REPLACE VIEW `SELINUX_ENABLED` AS select `host`.`selinux_enabled` AS `enabled`,count(`host`.`selinux_enabled`) AS `cnt` from `host` group by `host`.`selinux_enabled` order by count(`host`.`selinux_enabled`) desc;

CREATE OR REPLACE VIEW `SELINUX_ENFORCE` AS select `host`.`selinux_enforce` AS `enforce`,count(`host`.`selinux_enforce`) AS `cnt` from `host` group by `host`.`selinux_enforce` order by count(`host`.`selinux_enforce`) desc;

CREATE TABLE `file_systems` (
  `id` INT  NOT NULL AUTO_INCREMENT,
  `host_id` INT ,
  `mnt_pnt` VARCHAR(64) ,
  `fs_type` VARCHAR(16) ,
  `f_favail` INT ,
  `f_bsize` INT ,
  `f_frsize` INT ,
  `f_blocks` INT ,
  `f_bfree` INT ,
  `f_bavail` INT ,
  `f_files` INT ,
  `f_ffree` INT ,
  PRIMARY KEY (`id`),
  INDEX `host_id`(`host_id`)
)
ENGINE = MyISAM
CHARACTER SET utf8 COLLATE utf8_general_ci;

ALTER TABLE `smoon`.`file_systems` MODIFY COLUMN `id` BIGINT  NOT NULL DEFAULT NULL AUTO_INCREMENT;

alter table device modify column device_id int;

ALTER TABLE `device` CHARACTER SET utf8 COLLATE utf8_general_ci;

ALTER TABLE `classes` CHARACTER SET utf8 COLLATE utf8_general_ci;

ALTER TABLE `host` CHARACTER SET utf8 COLLATE utf8_general_ci;

ALTER TABLE `host_links` CHARACTER SET utf8 COLLATE utf8_general_ci;

ALTER TABLE `smoon`.`host` CHANGE COLUMN `selinux_enforce` `selinux_policy` VARCHAR(12) DEFAULT NULL;

CREATE OR REPLACE VIEW `SELINUX_POLICY` AS 
select `selinux_policy` AS `policy`, 
	count(`selinux_policy`) AS `cnt` 
from `host` 
group by policy 
order by count(policy) desc;

ALTER TABLE `smoon`.`host` ADD COLUMN `selinux_enforce` VARCHAR(12)  AFTER `selinux_policy`;

ALTER TABLE `smoon`.`host` CHANGE COLUMN `u_u_id` `uuid` VARCHAR(36)  NOT NULL,
 CHANGE COLUMN `o_s` `os` VARCHAR(32)  DEFAULT NULL,
 CHANGE COLUMN `num_cp_us` `num_cpus` INTEGER  DEFAULT NULL;

CREATE OR REPLACE VIEW `NUM_CPUS` AS select `host`.`num_cpus` AS `num_cpus`,count(`host`.`num_cpus`) AS `cnt` from `host` group by `host`.`num_cpus` order by count(`host`.`num_cpus`) desc

CREATE OR REPLACE VIEW `OS` AS select `host`.`os` AS `os`,count(`host`.`os`) AS `cnt` from `host` group by `host`.`os` order by count(`host`.`os`) desc


