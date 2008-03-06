ALTER TABLE `file_systems` ADD COLUMN `f_fssize` bigint(24) default NULL;


DROP TABLE IF EXISTS `FILESYSTEMS`;
/*!50001 DROP VIEW IF EXISTS `FILESYSTEMS`*/;
/*!50001 CREATE TABLE `FILESYSTEMS` (
  `fs_type` varchar(32),
  `cnt` bigint(21)
) */;


--
-- Final view structure for view `FILESYSTEMS`
--

/*!50001 DROP TABLE IF EXISTS `FILESYSTEMS`*/;
/*!50001 DROP VIEW IF EXISTS `FILESYSTEMS`*/;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`smoon`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `FILESYSTEMS` AS select `file_systems`.`fs_type` AS `fs_type`,count(`file_systems`.`fs_type`) AS `cnt` from `file_systems` group by `file_systems`.`fs_type` order by count(`file_systems`.`fs_type`) desc */;

