-- Add Index to last modified on host
create index last_modified on host (last_modified);

-- Add index to rating on host links
create index rating on host_links(rating, device_id);

-- Lengthen language to a proper size
alter table host modify column language varchar(15);
update host set language = concat(language, 'F-8') where language like '%.UT';

-- Lengthen selinux policy and enforcement strings
alter table host modify column selinux_policy varchar(25);
alter table host modify column selinux_enforce varchar(25);
update host set selinux_enforce='Not Installed' where selinux_enforce='Not Installe';
update host set selinux_policy='Not Installed' where selinux_policy='Not Installe';
