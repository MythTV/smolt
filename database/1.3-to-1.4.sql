-- 40 Seconds or so (depending on hardware and load)
create index fs_join_index on file_systems (host_id, fs_type);
-- 22 minutes (depending on hardware and load)
create index last_modified_join on host (id, last_modified);
-- 
create index device_host_link on host_links (device_id, host_link_id);
-- This one is a maybe, don't want to forget it
drop index class_2 on device;
