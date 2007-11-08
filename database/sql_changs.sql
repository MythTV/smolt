CREATE OR REPLACE VIEW `ARCH` AS Select platform, count(platform) as cnt from host group by platform order by cnt desc;
CREATE OR REPLACE VIEW `OS` AS Select o_s, count(o_s) as cnt from host group by o_s order by cnt desc;
CREATE OR REPLACE VIEW `RUNLEVEL` AS  select `host`.`default_runlevel` AS `default_runlevel`,count(`host`.`default_runlevel`) AS `cnt` from `host` group by `host`.`default_runlevel` order by count(`host`.`default_runlevel`) desc;
CREATE OR REPLACE VIEW `NUM_CPUS` AS SELECT  num_cp_us, count(num_cp_us) as cnt from host group by num_cp_us order by cnt desc;
CREATE OR REPLACE VIEW `VENDOR` AS Select vendor, count(vendor) as cnt from host where vendor != 'Unknown' and vendor != '' group by vendor order by cnt desc;
CREATE OR REPLACE VIEW `SYSTEM` AS Select system, count(system) as cnt from host where system != 'Unknown' and system != '' group by system order by cnt desc;
CREATE OR REPLACE VIEW `CPU_VENDOR` AS Select cpu_vendor, count(cpu_vendor) as cnt from host group by cpu_vendor order by cnt desc;
CREATE OR REPLACE VIEW `KERNEL_VERSION` AS SELECT kernel_version, count(kernel_version) as cnt from host group by kernel_version order by cnt desc;
CREATE OR REPLACE VIEW `FORMFACTOR` AS select formfactor, count(formfactor) as cnt from host group by formfactor order by cnt desc;
CREATE OR REPLACE VIEW `LANGUAGE` AS SELECT language, count(language) as cnt from host group by language order by cnt desc;
CREATE OR REPLACE VIEW `TOTALLIST` AS select device.description, count(host_links.device_id) as cnt from host_links, device where host_links.device_id=device.id group by host_links.device_id order by cnt desc;
CREATE OR REPLACE VIEW `UNIQUELIST` AS select device.description, count(distinct(host_links.host_link_id)) as cnt from host_links, device where host_links.device_id=device.id group by host_links.device_id order by cnt desc;

CREATE OR REPLACE VIEW `CLASS` AS select device.description, device.bus, device.driver, device.vendor_id, device.device_id, device.subsys_vendor_id, device.subsys_device_id, device.date_added, device.class, count(distinct(host_links.host_link_id)) as cnt from host_links, device where host_links.device_id=device.id group by host_links.device_id order by cnt desc;

ALTER TABLE `host_links` ADD INDEX `host_link_id`(`host_link_id`),
 ADD INDEX `device_id`(`device_id`);

ALTER TABLE `host` ADD COLUMN `rating` INT  NOT NULL DEFAULT 0 AFTER `last_modified`,
 ADD COLUMN `selinux_enabled` BOOL  NOT NULL DEFAULT false AFTER `rating`,
 ADD COLUMN `selinux_enforce` TEXT  DEFAULT NULL AFTER `selinux_enabled`;

DROP TABLE IF EXISTS `fas_link`;
CREATE TABLE `fas_link` (
  `id` INT  NOT NULL AUTO_INCREMENT,
  `u_u_id` VARCHAR(36)  NOT NULL,
  `user_name` VARCHAR(255)  NOT NULL,
  PRIMARY KEY (`id`)
);

update device set class = 'NONE' where class = 'None';

DROP TABLE IF EXISTS `classes`;
create table classes select distinct class from device; 

ALTER TABLE `classes`
 MODIFY COLUMN `class` VARCHAR(40) NOT NULL,
 ADD COLUMN `description` TEXT  DEFAULT NULL AFTER `class`,
 ADD PRIMARY KEY (`class`);

ALTER TABLE `host_links` ADD COLUMN `rating` INT  NOT NULL DEFAULT 0 AFTER `device_id`;

ALTER TABLE `device` DROP INDEX `description`,
 ADD UNIQUE INDEX `description` USING BTREE(`description`, `device_id`, `vendor_id`, `subsys_device_id`, `subsys_vendor_id`);

ALTER TABLE `device` MODIFY COLUMN class VARCHAR(40);
ALTER TABLE device ADD INDEX(class);


