-- MySQL dump 10.12
--
-- Host: localhost    Database: smoon_merr
-- ------------------------------------------------------
-- Server version	5.1.19-beta-Debian_1-log

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
-- Table structure for table `device`
--

DROP TABLE IF EXISTS `device`;
CREATE TABLE `device` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `description` varchar(128) NOT NULL DEFAULT '',
  `bus` text,
  `driver` text,
  `class` text,
  `date_added` datetime DEFAULT NULL,
  `device_id` varchar(16) DEFAULT NULL,
  `vendor_id` int(11) DEFAULT NULL,
  `subsys_device_id` int(11) DEFAULT NULL,
  `subsys_vendor_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `description` (`description`)
) ENGINE=MyISAM;

--
-- Table structure for table `host`
--

DROP TABLE IF EXISTS `host`;
CREATE TABLE `host` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `u_u_id` varchar(36) NOT NULL DEFAULT '',
  `o_s` text,
  `platform` text,
  `bogomips` double DEFAULT NULL,
  `system_memory` int(11) DEFAULT NULL,
  `system_swap` int(11) DEFAULT NULL,
  `vendor` text,
  `system` text,
  `cpu_vendor` text,
  `cpu_model` text,
  `num_cp_us` int(11) DEFAULT NULL,
  `cpu_speed` double DEFAULT NULL,
  `language` text,
  `default_runlevel` int(11) DEFAULT NULL,
  `kernel_version` text,
  `formfactor` text,
  `last_modified` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`id`),
  UNIQUE KEY `u_u_id` (`u_u_id`)
) ENGINE=MyISAM;

--
-- Table structure for table `host_links`
--

DROP TABLE IF EXISTS `host_links`;
CREATE TABLE `host_links` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `host_link_id` int(11) DEFAULT NULL,
  `device_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2007-09-09 22:23:13
