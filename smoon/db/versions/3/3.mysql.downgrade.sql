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
-- Final view structure for view `MYTHREMOTE`
--

/*!50001 DROP TABLE `MYTHREMOTE`*/;
/*!50001 DROP VIEW IF EXISTS `MYTHREMOTE`*/;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`smoon`@`%` SQL SECURITY DEFINER */
/*!50001 VIEW `MYTHREMOTE` AS select `host`.`mythremote` AS `mythremote`,count(`host`.`mythremote`) AS `cnt` from `host` group by `host`.`mythremote` order by count(`host`.`mythremote`) desc */;

--
-- Final view structure for view `MYTHTHEME`
--

/*!50001 DROP TABLE `MYTHTHEME`*/;
/*!50001 DROP VIEW IF EXISTS `MYTHTHEME`*/;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`smoon`@`%` SQL SECURITY DEFINER */
/*!50001 VIEW `MYTHTHEME` AS select `host`.`myththeme` AS `myththeme`,count(`host`.`myththeme`) AS `cnt` from `host` group by `host`.`myththeme` order by count(`host`.`myththeme`) desc */;

--
-- Final view structure for view `MYTH_SYSTEMROLE`
--

/*!50001 DROP TABLE `MYTH_SYSTEMROLE`*/;
/*!50001 DROP VIEW IF EXISTS `MYTH_SYSTEMROLE`*/;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`smoon`@`%` SQL SECURITY DEFINER */
/*!50001 VIEW `MYTH_SYSTEMROLE` AS select `host`.`myth_systemrole` AS `myth_systemrole`,count(`host`.`myth_systemrole`) AS `cnt` from `host` group by `host`.`myth_systemrole` order by count(`host`.`myth_systemrole`) desc */;

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
