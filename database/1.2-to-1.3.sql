alter table host modify column cpu_model varchar(80);
alter table host add column cpu_stepping int(11) DEFAULT NULL;
alter table host add column cpu_family int(11) DEFAULT NULL;
alter table host add column cpu_model_num int(11) DEFAULT NULL;
