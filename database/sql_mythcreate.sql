ALTER TABLE `host` ADD COLUMN `myth_systemrole` varchar(32) default NULL;
ALTER TABLE `host` ADD COLUMN `myththeme` varchar(32) default NULL;
ALTER TABLE `host` ADD COLUMN `mythremote` varchar(32) default NULL;


--
-- TABLE MYTH_SYSTEMROLE
--
DROP TABLE IF EXISTS `MYTH_SYSTEMROLE`;
/*!50001 DROP VIEW IF EXISTS `MYTH_SYSTEMROLE`*/;
/*!50001 CREATE TABLE `MYTH_SYSTEMROLE` (
  `myth_systemrole` varchar(32),
  `cnt` bigint(21)
) */;


--
-- Final view structure for view `MYTH_SYSTEMROLE`
--

/*!50001 DROP TABLE IF EXISTS `MYTH_SYSTEMROLE`*/;
/*!50001 DROP VIEW IF EXISTS `MYTH_SYSTEMROLE`*/;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50001 VIEW `MYTH_SYSTEMROLE` AS select `host`.`myth_systemrole` AS `myth_systemrole`,count(`host`.`myth_systemrole`) AS `cnt` from `host` group by `host`.`myth_systemrole` order by count(`host`.`myth_systemrole`) desc */;

--
-- TABLE MYTHREMOTE
--

DROP TABLE IF EXISTS `MYTHREMOTE`;
/*!50001 DROP VIEW IF EXISTS `MYTHREMOTE`*/;
/*!50001 CREATE TABLE `MYTHREMOTE` (
  `mythremote` varchar(32),
  `cnt` bigint(21)
) */;


--
-- Final view structure for view `MYTHREMOTE`
--

/*!50001 DROP TABLE IF EXISTS `MYTHREMOTE`*/;
/*!50001 DROP VIEW IF EXISTS `MYTHREMOTE`*/;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50001 VIEW `MYTHREMOTE` AS select `host`.`mythremote` AS `mythremote`,count(`host`.`mythremote`) AS `cnt` from `host` group by `host`.`mythremote` order by count(`host`.`mythremote`) desc */;

--
-- TABLE MYTHTHEME
--
DROP TABLE IF EXISTS `MYTHTHEME`;
/*!50001 DROP VIEW IF EXISTS `MYTHTHEME`*/;
/*!50001 CREATE TABLE `MYTHTHEME` (
  `myththeme` varchar(32),
  `cnt` bigint(21)
) */;


--
-- Final view structure for view `MYTHTHEME`
--

/*!50001 DROP TABLE IF EXISTS `MYTHTHEME`*/;
/*!50001 DROP VIEW IF EXISTS `MYTHTHEME`*/;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50001 VIEW `MYTHTHEME` AS select `host`.`myththeme` AS `myththeme`,count(`host`.`myththeme`) AS `cnt` from `host` group by `host`.`myththeme` order by count(`host`.`myththeme`) desc */;

