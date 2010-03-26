--
-- Table structure for table `host_archive`
--                                         

DROP TABLE IF EXISTS `host_archive`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;                  
CREATE TABLE `host_archive` (                     
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
-- Table structure for table `host_links_archive`
--                                               

DROP TABLE IF EXISTS `host_links_archive`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;                  
CREATE TABLE `host_links_archive` (               
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


