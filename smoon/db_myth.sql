alter table host add column myth_remote text(32);
alter table host add column myth_theme text(32);
alter table host add column myth_role text(32);
alter table host add column myth_plugins text(32);
alter table host add column myth_tuner int;
create VIEW `MYTH_REMOTE` AS select `host`.`myth_remote` AS `myth_remote`,count(`host`.`myth_remote`) AS `cnt` from `host` group by `host`.`myth_remote` order by count(`host`.`myth_remote`);
