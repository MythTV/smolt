-- MySQL dump 10.11
--
-- Host: localhost    Database: smoon
-- ------------------------------------------------------
-- Server version	5.0.45

--
-- Table structure for table classes
--

DROP TABLE IF EXISTS classes;
CREATE TABLE classes (
  class varchar(40) NOT NULL,
  description varchar(64) default NULL,
  PRIMARY KEY  (class)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Table structure for table device
--

DROP TABLE IF EXISTS device;
CREATE TABLE device (
  id int(11) NOT NULL auto_increment,
  description varchar(128) NOT NULL default '',
  bus varchar(8) default NULL,
  driver varchar(16) default NULL,
  class varchar(40) default NULL,
  date_added datetime default NULL,
  device_id varchar(16) default NULL,
  vendor_id int(11) default NULL,
  subsys_device_id int(11) default NULL,
  subsys_vendor_id int(11) default NULL,
  PRIMARY KEY  (id),
  UNIQUE KEY description USING BTREE (description,device_id,vendor_id,subsys_device_id,subsys_vendor_id),
  KEY class (class),
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Table structure for table fas_link
--

DROP TABLE IF EXISTS fas_link;
CREATE TABLE fas_link (
  id int(11) NOT NULL auto_increment,
  u_u_id varchar(36) NOT NULL,
  user_name varchar(255) NOT NULL,
  PRIMARY KEY  (id)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Table structure for table host
--

DROP TABLE IF EXISTS host;
CREATE TABLE host (
  id int(11) NOT NULL auto_increment,
  u_u_id varchar(36) NOT NULL default '',
  o_s varchar(32) default NULL,
  platform varchar(16) default NULL,
  bogomips double default NULL,
  system_memory int(11) default NULL,
  system_swap int(11) default NULL,
  vendor varchar(96) default NULL,
  system varchar(96) default NULL,
  cpu_vendor varchar(32) default NULL,
  cpu_model varchar(32) default NULL,
  num_cp_us int(11) default NULL,
  cpu_speed double default NULL,
  language varchar(8) default NULL,
  default_runlevel int(11) default NULL,
  kernel_version varchar(32) default NULL,
  formfactor varchar(32) default NULL,
  last_modified datetime NOT NULL default '0000-00-00 00:00:00',
  rating int(11) NOT NULL default '0',
  selinux_enabled tinyint(1) NOT NULL default '0',
  selinux_enforce varchar(12) default NULL,
  PRIMARY KEY  (id),
  UNIQUE KEY u_u_id (u_u_id),
  KEY platform (platform)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Table structure for table host_links
--

DROP TABLE IF EXISTS host_links;
CREATE TABLE host_links (
  id int(11) NOT NULL auto_increment,
  host_link_id int(11) default NULL,
  device_id int(11) default NULL,
  rating int(11) NOT NULL default '0',
  PRIMARY KEY  (id),
  KEY host_link_id (host_link_id),
  KEY device_id (device_id)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Final view structure for view ARCH
--

/*!50001 DROP TABLE IF EXISTS ARCH*/;
/*!50001 DROP VIEW IF EXISTS ARCH*/;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50001 VIEW ARCH AS select host.platform AS platform,count(host.platform) AS cnt from host group by host.platform order by count(host.platform) desc */;

--
-- Final view structure for view CLASS
--

/*!50001 DROP TABLE IF EXISTS CLASS*/;
/*!50001 DROP VIEW IF EXISTS CLASS*/;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50001 VIEW CLASS AS select device.description AS description,device.bus AS bus,device.driver AS driver,device.vendor_id AS vendor_id,device.device_id AS device_id,device.subsys_vendor_id AS subsys_vendor_id,device.subsys_device_id AS subsys_device_id,device.date_added AS date_added,device.class AS class,count(distinct host_links.host_link_id) AS cnt from (host_links join device) where (host_links.device_id = device.id) group by host_links.device_id order by count(distinct host_links.host_link_id) desc */;

--
-- Final view structure for view CPU_VENDOR
--

/*!50001 DROP TABLE IF EXISTS CPU_VENDOR*/;
/*!50001 DROP VIEW IF EXISTS CPU_VENDOR*/;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50001 VIEW CPU_VENDOR AS select host.cpu_vendor AS cpu_vendor,count(host.cpu_vendor) AS cnt from host group by host.cpu_vendor order by count(host.cpu_vendor) desc */;

--
-- Final view structure for view FORMFACTOR
--

/*!50001 DROP TABLE IF EXISTS FORMFACTOR*/;
/*!50001 DROP VIEW IF EXISTS FORMFACTOR*/;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50001 VIEW FORMFACTOR AS select host.formfactor AS formfactor,count(host.formfactor) AS cnt from host group by host.formfactor order by count(host.formfactor) desc */;

--
-- Final view structure for view KERNEL_VERSION
--

/*!50001 DROP TABLE IF EXISTS KERNEL_VERSION*/;
/*!50001 DROP VIEW IF EXISTS KERNEL_VERSION*/;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50001 VIEW KERNEL_VERSION AS select host.kernel_version AS kernel_version,count(host.kernel_version) AS cnt from host group by host.kernel_version order by count(host.kernel_version) desc */;

--
-- Final view structure for view LANGUAGE
--

/*!50001 DROP TABLE IF EXISTS LANGUAGE*/;
/*!50001 DROP VIEW IF EXISTS LANGUAGE*/;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50001 VIEW LANGUAGE AS select host.language AS language,count(host.language) AS cnt from host group by host.language order by count(host.language) desc */;

--
-- Final view structure for view NUM_CPUS
--

/*!50001 DROP TABLE IF EXISTS NUM_CPUS*/;
/*!50001 DROP VIEW IF EXISTS NUM_CPUS*/;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50001 VIEW NUM_CPUS AS select host.num_cp_us AS num_cp_us,count(host.num_cp_us) AS cnt from host group by host.num_cp_us order by count(host.num_cp_us) desc */;

--
-- Final view structure for view OS
--

/*!50001 DROP TABLE IF EXISTS OS*/;
/*!50001 DROP VIEW IF EXISTS OS*/;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50001 VIEW OS AS select host.o_s AS o_s,count(host.o_s) AS cnt from host group by host.o_s order by count(host.o_s) desc */;

--
-- Final view structure for view RUNLEVEL
--

/*!50001 DROP TABLE IF EXISTS RUNLEVEL*/;
/*!50001 DROP VIEW IF EXISTS RUNLEVEL*/;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50001 VIEW RUNLEVEL AS select host.default_runlevel AS default_runlevel,count(host.default_runlevel) AS cnt from host group by host.default_runlevel order by count(host.default_runlevel) desc */;

--
-- Final view structure for view SYSTEM
--

/*!50001 DROP TABLE IF EXISTS SYSTEM*/;
/*!50001 DROP VIEW IF EXISTS SYSTEM*/;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50001 VIEW SYSTEM AS select host.system AS system,count(host.system) AS cnt from host where ((host.system <> _latin1'Unknown') and (host.system <> _latin1'')) group by host.system order by count(host.system) desc */;

--
-- Final view structure for view TOTALLIST
--

/*!50001 DROP TABLE IF EXISTS TOTALLIST*/;
/*!50001 DROP VIEW IF EXISTS TOTALLIST*/;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50001 VIEW TOTALLIST AS select device.description AS description,count(host_links.device_id) AS cnt from (host_links join device) where (host_links.device_id = device.id) group by host_links.device_id order by count(host_links.device_id) desc */;

--
-- Final view structure for view UNIQUELIST
--

/*!50001 DROP TABLE IF EXISTS UNIQUELIST*/;
/*!50001 DROP VIEW IF EXISTS UNIQUELIST*/;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50001 VIEW UNIQUELIST AS select device.description AS description,count(distinct host_links.host_link_id) AS cnt from (host_links join device) where (host_links.device_id = device.id) group by host_links.device_id order by count(distinct host_links.host_link_id) desc */;

--
-- Final view structure for view VENDOR
--

/*!50001 DROP TABLE IF EXISTS VENDOR*/;
/*!50001 DROP VIEW IF EXISTS VENDOR*/;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50001 VIEW VENDOR AS select host.vendor AS vendor,count(host.vendor) AS cnt from host where ((host.vendor <> _latin1'Unknown') and (host.vendor <> _latin1'')) group by host.vendor order by count(host.vendor) desc */;

-- Dump completed on 2007-12-14 22:20:12
