-- 40 Seconds or so (depending on hardware and load)
create index fs_join_index on file_systems (host_id, fs_type);
-- 22 minutes (depending on hardware and load)
create index last_modified_join on host (id, last_modified);
-- This is a duplicate, dropping 5 seconds
drop index class_2 on device;
