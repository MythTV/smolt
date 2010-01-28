-- MySQL dump 10.11
--
-- Host: localhost    Database: smolt
-- ------------------------------------------------------
-- Server version	5.0.77-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Temporary table structure for view `ARCH`
--

DROP TABLE IF EXISTS `ARCH`;
/*!50001 DROP VIEW IF EXISTS `ARCH`*/;
/*!50001 CREATE TABLE `ARCH` (
  `platform` varchar(16),
  `cnt` bigint(21)
) ENGINE=MyISAM */;

--
-- Temporary table structure for view `CLASS`
--

DROP TABLE IF EXISTS `CLASS`;
/*!50001 DROP VIEW IF EXISTS `CLASS`*/;
/*!50001 CREATE TABLE `CLASS` (
  `description` varchar(128),
  `bus` varchar(8),
  `driver` varchar(16),
  `vendor_id` int(11),
  `device_id` int(11),
  `subsys_vendor_id` int(11),
  `subsys_device_id` int(11),
  `date_added` datetime,
  `class` varchar(40),
  `cnt` bigint(21)
) ENGINE=MyISAM */;

--
-- Temporary table structure for view `CPU_VENDOR`
--

DROP TABLE IF EXISTS `CPU_VENDOR`;
/*!50001 DROP VIEW IF EXISTS `CPU_VENDOR`*/;
/*!50001 CREATE TABLE `CPU_VENDOR` (
  `cpu_vendor` varchar(32),
  `cnt` bigint(21)
) ENGINE=MyISAM */;

--
-- Temporary table structure for view `FILESYSTEMS`
--

DROP TABLE IF EXISTS `FILESYSTEMS`;
/*!50001 DROP VIEW IF EXISTS `FILESYSTEMS`*/;
/*!50001 CREATE TABLE `FILESYSTEMS` (
  `fs_type` varchar(16),
  `cnt` bigint(21)
) ENGINE=MyISAM */;

--
-- Temporary table structure for view `FORMFACTOR`
--

DROP TABLE IF EXISTS `FORMFACTOR`;
/*!50001 DROP VIEW IF EXISTS `FORMFACTOR`*/;
/*!50001 CREATE TABLE `FORMFACTOR` (
  `formfactor` varchar(32),
  `cnt` bigint(21)
) ENGINE=MyISAM */;

--
-- Temporary table structure for view `KERNEL_VERSION`
--

DROP TABLE IF EXISTS `KERNEL_VERSION`;
/*!50001 DROP VIEW IF EXISTS `KERNEL_VERSION`*/;
/*!50001 CREATE TABLE `KERNEL_VERSION` (
  `kernel_version` varchar(32),
  `cnt` bigint(21)
) ENGINE=MyISAM */;

--
-- Temporary table structure for view `LANGUAGE`
--

DROP TABLE IF EXISTS `LANGUAGE`;
/*!50001 DROP VIEW IF EXISTS `LANGUAGE`*/;
/*!50001 CREATE TABLE `LANGUAGE` (
  `language` varchar(15),
  `cnt` bigint(21)
) ENGINE=MyISAM */;

--
-- Temporary table structure for view `NUM_CPUS`
--

DROP TABLE IF EXISTS `NUM_CPUS`;
/*!50001 DROP VIEW IF EXISTS `NUM_CPUS`*/;
/*!50001 CREATE TABLE `NUM_CPUS` (
  `num_cpus` int(11),
  `cnt` bigint(21)
) ENGINE=MyISAM */;

--
-- Temporary table structure for view `OS`
--

DROP TABLE IF EXISTS `OS`;
/*!50001 DROP VIEW IF EXISTS `OS`*/;
/*!50001 CREATE TABLE `OS` (
  `os` varchar(32),
  `cnt` bigint(21)
) ENGINE=MyISAM */;

--
-- Temporary table structure for view `RUNLEVEL`
--

DROP TABLE IF EXISTS `RUNLEVEL`;
/*!50001 DROP VIEW IF EXISTS `RUNLEVEL`*/;
/*!50001 CREATE TABLE `RUNLEVEL` (
  `default_runlevel` int(11),
  `cnt` bigint(21)
) ENGINE=MyISAM */;

--
-- Temporary table structure for view `SELINUX_ENABLED`
--

DROP TABLE IF EXISTS `SELINUX_ENABLED`;
/*!50001 DROP VIEW IF EXISTS `SELINUX_ENABLED`*/;
/*!50001 CREATE TABLE `SELINUX_ENABLED` (
  `enabled` tinyint(1),
  `cnt` bigint(21)
) ENGINE=MyISAM */;

--
-- Temporary table structure for view `SELINUX_ENFORCE`
--

DROP TABLE IF EXISTS `SELINUX_ENFORCE`;
/*!50001 DROP VIEW IF EXISTS `SELINUX_ENFORCE`*/;
/*!50001 CREATE TABLE `SELINUX_ENFORCE` (
  `enforce` varchar(25),
  `cnt` bigint(21)
) ENGINE=MyISAM */;

--
-- Temporary table structure for view `SELINUX_POLICY`
--

DROP TABLE IF EXISTS `SELINUX_POLICY`;
/*!50001 DROP VIEW IF EXISTS `SELINUX_POLICY`*/;
/*!50001 CREATE TABLE `SELINUX_POLICY` (
  `policy` varchar(25),
  `cnt` bigint(21)
) ENGINE=MyISAM */;

--
-- Temporary table structure for view `SYSTEM`
--

DROP TABLE IF EXISTS `SYSTEM`;
/*!50001 DROP VIEW IF EXISTS `SYSTEM`*/;
/*!50001 CREATE TABLE `SYSTEM` (
  `system` varchar(96),
  `cnt` bigint(21)
) ENGINE=MyISAM */;

--
-- Temporary table structure for view `TOTALLIST`
--

DROP TABLE IF EXISTS `TOTALLIST`;
/*!50001 DROP VIEW IF EXISTS `TOTALLIST`*/;
/*!50001 CREATE TABLE `TOTALLIST` (
  `description` varchar(128),
  `cnt` bigint(21)
) ENGINE=MyISAM */;

--
-- Temporary table structure for view `UNIQUELIST`
--

DROP TABLE IF EXISTS `UNIQUELIST`;
/*!50001 DROP VIEW IF EXISTS `UNIQUELIST`*/;
/*!50001 CREATE TABLE `UNIQUELIST` (
  `description` varchar(128),
  `cnt` bigint(21)
) ENGINE=MyISAM */;

--
-- Temporary table structure for view `VENDOR`
--

DROP TABLE IF EXISTS `VENDOR`;
/*!50001 DROP VIEW IF EXISTS `VENDOR`*/;
/*!50001 CREATE TABLE `VENDOR` (
  `vendor` varchar(96),
  `cnt` bigint(21)
) ENGINE=MyISAM */;

--
-- Table structure for table `classes`
--

DROP TABLE IF EXISTS `classes`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `classes` (
  `class` varchar(40) character set latin1 NOT NULL,
  `description` varchar(64) character set latin1 default NULL,
  PRIMARY KEY  (`class`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `device`
--

DROP TABLE IF EXISTS `device`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `device` (
  `id` int(11) NOT NULL auto_increment,
  `description` varchar(128) character set latin1 NOT NULL default '',
  `bus` varchar(8) character set latin1 default NULL,
  `driver` varchar(16) character set latin1 default NULL,
  `class` varchar(40) character set latin1 default NULL,
  `date_added` datetime default NULL,
  `device_id` int(11) default NULL,
  `vendor_id` int(11) default NULL,
  `subsys_device_id` int(11) default NULL,
  `subsys_vendor_id` int(11) default NULL,
  PRIMARY KEY  (`id`),
  UNIQUE KEY `description` USING BTREE (`description`,`device_id`,`vendor_id`,`subsys_device_id`,`subsys_vendor_id`),
  KEY `class` (`class`)
) ENGINE=MyISAM AUTO_INCREMENT=237139 DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `fas_link`
--

DROP TABLE IF EXISTS `fas_link`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `fas_link` (
  `id` int(11) NOT NULL auto_increment,
  `uuid` varchar(36) default NULL,
  `user_name` varchar(255) NOT NULL,
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `file_systems`
--

DROP TABLE IF EXISTS `file_systems`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `file_systems` (
  `id` bigint(20) NOT NULL auto_increment,
  `host_id` int(11) default NULL,
  `mnt_pnt` varchar(64) default NULL,
  `fs_type` varchar(16) default NULL,
  `f_favail` int(11) default NULL,
  `f_bsize` bigint(20) default NULL,
  `f_frsize` bigint(20) default NULL,
  `f_blocks` int(11) default NULL,
  `f_bfree` int(11) default NULL,
  `f_bavail` int(11) default NULL,
  `f_files` int(11) default NULL,
  `f_ffree` int(11) default NULL,
  `f_fssize` bigint(24) default NULL,
  PRIMARY KEY  (`id`),
  KEY `host_id` (`host_id`),
  KEY `fs_join_index` (`host_id`,`fs_type`)
) ENGINE=MyISAM AUTO_INCREMENT=6147005 DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `host`
--

DROP TABLE IF EXISTS `host`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `host` (
  `id` int(11) NOT NULL auto_increment,
  `uuid` varchar(36) NOT NULL,
  `pub_uuid` varchar(40) character set latin1 NOT NULL,
  `os` varchar(32) default NULL,
  `platform` varchar(16) character set latin1 default NULL,
  `bogomips` double default NULL,
  `system_memory` int(11) default NULL,
  `system_swap` int(11) default NULL,
  `vendor` varchar(96) character set latin1 default NULL,
  `system` varchar(96) character set latin1 default NULL,
  `cpu_vendor` varchar(32) character set latin1 default NULL,
  `cpu_model` varchar(80) default NULL,
  `num_cpus` int(11) default NULL,
  `cpu_speed` double default NULL,
  `language` varchar(15) default NULL,
  `default_runlevel` int(11) default NULL,
  `kernel_version` varchar(32) character set latin1 default NULL,
  `formfactor` varchar(32) character set latin1 default NULL,
  `last_modified` datetime NOT NULL default '0000-00-00 00:00:00',
  `rating` int(11) NOT NULL default '0',
  `selinux_enabled` tinyint(1) NOT NULL default '0',
  `selinux_policy` varchar(25) default NULL,
  `selinux_enforce` varchar(25) default NULL,
  `cpu_stepping` int(11) default NULL,
  `cpu_family` int(11) default NULL,
  `cpu_model_num` int(11) default NULL,
  PRIMARY KEY  (`id`),
  UNIQUE KEY `u_u_id` (`uuid`),
  KEY `platform` (`platform`),
  KEY `pub_uuid` (`pub_uuid`),
  KEY `last_modified` (`last_modified`),
  KEY `last_modified_join` (`id`,`last_modified`)
) ENGINE=InnoDB AUTO_INCREMENT=1735597 DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `host_links`
--

DROP TABLE IF EXISTS `host_links`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `host_links` (
  `id` int(11) NOT NULL auto_increment,
  `host_link_id` int(11) default NULL,
  `device_id` int(11) default NULL,
  `rating` int(11) NOT NULL default '0',
  PRIMARY KEY  (`id`),
  KEY `host_link_id` (`host_link_id`),
  KEY `device_id` (`device_id`),
  KEY `rating` (`rating`,`device_id`),
  KEY `device_host_link` (`device_id`,`host_link_id`)
) ENGINE=MyISAM AUTO_INCREMENT=112099123 DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Final view structure for view `ARCH`
--

/*!50001 DROP TABLE `ARCH`*/;
/*!50001 DROP VIEW IF EXISTS `ARCH`*/;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `ARCH` AS select `host`.`platform` AS `platform`,count(`host`.`platform`) AS `cnt` from `host` group by `host`.`platform` order by count(`host`.`platform`) desc */;

--
-- Final view structure for view `CLASS`
--

/*!50001 DROP TABLE `CLASS`*/;
/*!50001 DROP VIEW IF EXISTS `CLASS`*/;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `CLASS` AS select `device`.`description` AS `description`,`device`.`bus` AS `bus`,`device`.`driver` AS `driver`,`device`.`vendor_id` AS `vendor_id`,`device`.`device_id` AS `device_id`,`device`.`subsys_vendor_id` AS `subsys_vendor_id`,`device`.`subsys_device_id` AS `subsys_device_id`,`device`.`date_added` AS `date_added`,`device`.`class` AS `class`,count(distinct `host_links`.`host_link_id`) AS `cnt` from (`host_links` join `device`) where (`host_links`.`device_id` = `device`.`id`) group by `host_links`.`device_id` order by count(distinct `host_links`.`host_link_id`) desc */;

--
-- Final view structure for view `CPU_VENDOR`
--

/*!50001 DROP TABLE `CPU_VENDOR`*/;
/*!50001 DROP VIEW IF EXISTS `CPU_VENDOR`*/;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `CPU_VENDOR` AS select `host`.`cpu_vendor` AS `cpu_vendor`,count(`host`.`cpu_vendor`) AS `cnt` from `host` group by `host`.`cpu_vendor` order by count(`host`.`cpu_vendor`) desc */;

--
-- Final view structure for view `FILESYSTEMS`
--

/*!50001 DROP TABLE `FILESYSTEMS`*/;
/*!50001 DROP VIEW IF EXISTS `FILESYSTEMS`*/;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `FILESYSTEMS` AS select `file_systems`.`fs_type` AS `fs_type`,count(`file_systems`.`fs_type`) AS `cnt` from `file_systems` group by `file_systems`.`fs_type` order by count(`file_systems`.`fs_type`) desc */;

--
-- Final view structure for view `FORMFACTOR`
--

/*!50001 DROP TABLE `FORMFACTOR`*/;
/*!50001 DROP VIEW IF EXISTS `FORMFACTOR`*/;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `FORMFACTOR` AS select `host`.`formfactor` AS `formfactor`,count(`host`.`formfactor`) AS `cnt` from `host` group by `host`.`formfactor` order by count(`host`.`formfactor`) desc */;

--
-- Final view structure for view `KERNEL_VERSION`
--

/*!50001 DROP TABLE `KERNEL_VERSION`*/;
/*!50001 DROP VIEW IF EXISTS `KERNEL_VERSION`*/;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `KERNEL_VERSION` AS select `host`.`kernel_version` AS `kernel_version`,count(`host`.`kernel_version`) AS `cnt` from `host` group by `host`.`kernel_version` order by count(`host`.`kernel_version`) desc */;

--
-- Final view structure for view `LANGUAGE`
--

/*!50001 DROP TABLE `LANGUAGE`*/;
/*!50001 DROP VIEW IF EXISTS `LANGUAGE`*/;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `LANGUAGE` AS select `host`.`language` AS `language`,count(`host`.`language`) AS `cnt` from `host` group by `host`.`language` order by count(`host`.`language`) desc */;

--
-- Final view structure for view `NUM_CPUS`
--

/*!50001 DROP TABLE `NUM_CPUS`*/;
/*!50001 DROP VIEW IF EXISTS `NUM_CPUS`*/;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `NUM_CPUS` AS select `host`.`num_cpus` AS `num_cpus`,count(`host`.`num_cpus`) AS `cnt` from `host` group by `host`.`num_cpus` order by count(`host`.`num_cpus`) desc */;

--
-- Final view structure for view `OS`
--

/*!50001 DROP TABLE `OS`*/;
/*!50001 DROP VIEW IF EXISTS `OS`*/;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `OS` AS select `host`.`os` AS `os`,count(`host`.`os`) AS `cnt` from `host` group by `host`.`os` order by count(`host`.`os`) desc */;

--
-- Final view structure for view `RUNLEVEL`
--

/*!50001 DROP TABLE `RUNLEVEL`*/;
/*!50001 DROP VIEW IF EXISTS `RUNLEVEL`*/;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `RUNLEVEL` AS select `host`.`default_runlevel` AS `default_runlevel`,count(`host`.`default_runlevel`) AS `cnt` from `host` group by `host`.`default_runlevel` order by count(`host`.`default_runlevel`) desc */;

--
-- Final view structure for view `SELINUX_ENABLED`
--

/*!50001 DROP TABLE `SELINUX_ENABLED`*/;
/*!50001 DROP VIEW IF EXISTS `SELINUX_ENABLED`*/;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `SELINUX_ENABLED` AS select `host`.`selinux_enabled` AS `enabled`,count(`host`.`selinux_enabled`) AS `cnt` from `host` group by `host`.`selinux_enabled` order by count(`host`.`selinux_enabled`) desc */;

--
-- Final view structure for view `SELINUX_ENFORCE`
--

/*!50001 DROP TABLE `SELINUX_ENFORCE`*/;
/*!50001 DROP VIEW IF EXISTS `SELINUX_ENFORCE`*/;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `SELINUX_ENFORCE` AS select `host`.`selinux_enforce` AS `enforce`,count(`host`.`selinux_enforce`) AS `cnt` from `host` group by `host`.`selinux_enforce` order by count(`host`.`selinux_enforce`) desc */;

--
-- Final view structure for view `SELINUX_POLICY`
--

/*!50001 DROP TABLE `SELINUX_POLICY`*/;
/*!50001 DROP VIEW IF EXISTS `SELINUX_POLICY`*/;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `SELINUX_POLICY` AS select `host`.`selinux_policy` AS `policy`,count(`host`.`selinux_policy`) AS `cnt` from `host` group by `host`.`selinux_policy` order by count(`host`.`selinux_policy`) desc */;

--
-- Final view structure for view `SYSTEM`
--

/*!50001 DROP TABLE `SYSTEM`*/;
/*!50001 DROP VIEW IF EXISTS `SYSTEM`*/;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `SYSTEM` AS select `host`.`system` AS `system`,count(`host`.`system`) AS `cnt` from `host` where ((`host`.`system` <> _latin1'Unknown') and (`host`.`system` <> _latin1'')) group by `host`.`system` order by count(`host`.`system`) desc */;

--
-- Final view structure for view `TOTALLIST`
--

/*!50001 DROP TABLE `TOTALLIST`*/;
/*!50001 DROP VIEW IF EXISTS `TOTALLIST`*/;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `TOTALLIST` AS select `device`.`description` AS `description`,count(`host_links`.`device_id`) AS `cnt` from (`host_links` join `device`) where (`host_links`.`device_id` = `device`.`id`) group by `host_links`.`device_id` order by count(`host_links`.`device_id`) desc */;

--
-- Final view structure for view `UNIQUELIST`
--

/*!50001 DROP TABLE `UNIQUELIST`*/;
/*!50001 DROP VIEW IF EXISTS `UNIQUELIST`*/;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `UNIQUELIST` AS select `device`.`description` AS `description`,count(distinct `host_links`.`host_link_id`) AS `cnt` from (`host_links` join `device`) where (`host_links`.`device_id` = `device`.`id`) group by `host_links`.`device_id` order by count(distinct `host_links`.`host_link_id`) desc */;

--
-- Final view structure for view `VENDOR`
--

/*!50001 DROP TABLE `VENDOR`*/;
/*!50001 DROP VIEW IF EXISTS `VENDOR`*/;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `VENDOR` AS select `host`.`vendor` AS `vendor`,count(`host`.`vendor`) AS `cnt` from `host` where ((`host`.`vendor` <> _latin1'Unknown') and (`host`.`vendor` <> _latin1'')) group by `host`.`vendor` order by count(`host`.`vendor`) desc */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2010-01-14 16:33:44
