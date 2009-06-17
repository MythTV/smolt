-- MySQL dump 10.13  Distrib 5.1.32, for redhat-linux-gnu (x86_64)
--
-- Host: localhost    Database: smolt
-- ------------------------------------------------------
-- Server version	5.1.32-log

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
-- Table structure for table `classes`
--

DROP TABLE IF EXISTS `classes`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `classes` (
  `class` varchar(40) CHARACTER SET latin1 NOT NULL,
  `description` varchar(64) CHARACTER SET latin1 DEFAULT NULL,
  PRIMARY KEY (`class`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `device`
--

DROP TABLE IF EXISTS `device`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `device` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `description` varchar(128) CHARACTER SET latin1 NOT NULL DEFAULT '',
  `bus` varchar(8) CHARACTER SET latin1 DEFAULT NULL,
  `driver` varchar(16) CHARACTER SET latin1 DEFAULT NULL,
  `class` varchar(40) CHARACTER SET latin1 DEFAULT NULL,
  `date_added` datetime DEFAULT NULL,
  `device_id` int(11) DEFAULT NULL,
  `vendor_id` int(11) DEFAULT NULL,
  `subsys_device_id` int(11) DEFAULT NULL,
  `subsys_vendor_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `description` (`description`,`device_id`,`vendor_id`,`subsys_device_id`,`subsys_vendor_id`) USING BTREE,
  KEY `class` (`class`),
  KEY `class_2` (`class`)
) ENGINE=MyISAM AUTO_INCREMENT=213515 DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `fas_link`
--

DROP TABLE IF EXISTS `fas_link`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `fas_link` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uuid` varchar(36) DEFAULT NULL,
  `user_name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `file_systems`
--

DROP TABLE IF EXISTS `file_systems`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `file_systems` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `host_id` int(11) DEFAULT NULL,
  `mnt_pnt` varchar(64) DEFAULT NULL,
  `fs_type` varchar(16) DEFAULT NULL,
  `f_favail` int(11) DEFAULT NULL,
  `f_bsize` int(11) DEFAULT NULL,
  `f_frsize` int(11) DEFAULT NULL,
  `f_blocks` int(11) DEFAULT NULL,
  `f_bfree` int(11) DEFAULT NULL,
  `f_bavail` int(11) DEFAULT NULL,
  `f_files` int(11) DEFAULT NULL,
  `f_ffree` int(11) DEFAULT NULL,
  `f_fssize` bigint(24) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `host_id` (`host_id`)
) ENGINE=MyISAM AUTO_INCREMENT=3731964 DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `host`
--

DROP TABLE IF EXISTS `host`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `host` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uuid` varchar(36) NOT NULL,
  `pub_uuid` varchar(40) CHARACTER SET latin1 NOT NULL,
  `os` varchar(32) DEFAULT NULL,
  `platform` varchar(16) CHARACTER SET latin1 DEFAULT NULL,
  `bogomips` double DEFAULT NULL,
  `system_memory` int(11) DEFAULT NULL,
  `system_swap` int(11) DEFAULT NULL,
  `vendor` varchar(96) CHARACTER SET latin1 DEFAULT NULL,
  `system` varchar(96) CHARACTER SET latin1 DEFAULT NULL,
  `cpu_vendor` varchar(32) CHARACTER SET latin1 DEFAULT NULL,
  `cpu_model` varchar(80) DEFAULT NULL,
  `num_cpus` int(11) DEFAULT NULL,
  `cpu_speed` double DEFAULT NULL,
  `language` varchar(15) DEFAULT NULL,
  `default_runlevel` int(11) DEFAULT NULL,
  `kernel_version` varchar(32) CHARACTER SET latin1 DEFAULT NULL,
  `formfactor` varchar(32) CHARACTER SET latin1 DEFAULT NULL,
  `last_modified` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  `rating` int(11) NOT NULL DEFAULT '0',
  `selinux_enabled` tinyint(1) NOT NULL DEFAULT '0',
  `selinux_policy` varchar(25) DEFAULT NULL,
  `selinux_enforce` varchar(25) DEFAULT NULL,
  `cpu_stepping` int(11) DEFAULT NULL,
  `cpu_family` int(11) DEFAULT NULL,
  `cpu_model_num` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `u_u_id` (`uuid`),
  KEY `platform` (`platform`),
  KEY `pub_uuid` (`pub_uuid`),
  KEY `last_modified` (`last_modified`)
) ENGINE=MyISAM AUTO_INCREMENT=1262260 DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `host_links`
--

DROP TABLE IF EXISTS `host_links`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `host_links` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `host_link_id` int(11) DEFAULT NULL,
  `device_id` int(11) DEFAULT NULL,
  `rating` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `host_link_id` (`host_link_id`),
  KEY `device_id` (`device_id`),
  KEY `rating` (`rating`,`device_id`)
) ENGINE=MyISAM AUTO_INCREMENT=79815279 DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2009-06-17 21:11:46
