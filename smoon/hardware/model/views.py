from sqlalchemy import *

from hardware.model.model import *

def column_cnt(column):
    '''This is a counted column.  A convenience function'''
    return func.count(column).label('cnt')

def column_cnt_d(column):
    '''The same as column_cnt, but distinct'''
    return func.count(func.distinct(column)).label('cnt')

def counted_view(name, columns, cnt_obj, group_by, restrictions=None, desc=False):
    '''Generates a satistical counted view of some table or simple join 
    for some group of columns.
    
    This function is a bit low level, and you probably want the
    simple version of this: simple_mapped_counted_view
    
    params:
        name is the name of the view
        columns is an iterable with the columns desired
            - multiple tables' columns may be used here, for simple joins
        cnt_obj is the object the count is performed on
        group_by the object to group on, such that it is counted
        restrictions are sqlalchemy where constraints
        desc is a boolean whether you want it in ascending, descending or condescending order
    '''
    s = select(columns + [cnt_obj], restrictions).group_by(group_by)
    if desc:
        return s.order_by(cnt_obj.desc()).alias(name)
    else:
        return s.order_by(cnt_obj).alias(name)

def simple_counted_view(name, column, desc=False, label=None):
    '''Generates a counted view on a single column'''
    cnt_obj = column_cnt(column)
    if label:
        column = column.label(label)
    sel = counted_view(name, [column], cnt_obj, column, desc=desc)
    return (cnt_obj, sel)

#This creates one ugly sideeffect, but I couldn't think of a better way off hand
#that doesn't require a sever language adjustment :p -ynemoy
def simple_mapped_counted_view(name, column, map_obj, desc=False, label=None):
    '''For some column in a table, generates a counted view and maps it to some object
    
    params:
        name is the name of the view
        column is the column being counted
        map_obj is the object to be mapped to
        desc is the order you want it in
        label renames the column name to something else, so the class
            uses a different attribute name than the source table
    '''
    cnt_obj, sel = simple_counted_view(name, column, desc, label)
    if label:
        p_key = getattr(sel.c, label)
    else:
        p_key = getattr(sel.c, column.name)
    mapper(map_obj, sel, primary_key=[p_key])
    return sel
    

tot_device_cnt = func.count(host_links.c.device_id).label('cnt')
totallist = select([computer_logical_devices.c.description, tot_device_cnt], 
                   host_links.c.device_id==computer_logical_devices.c.id)\
                   .group_by(host_links.c.device_id)\
                   .order_by(tot_device_cnt)\
                   .alias('TOTALLIST')

unq_device_cnt = func.count(distinct(host_links.c.device_id)).label('cnt')
uniquelist = select([computer_logical_devices.c.description, unq_device_cnt], 
                   host_links.c.device_id==computer_logical_devices.c.id)\
                   .group_by(host_links.c.device_id)\
                   .order_by(unq_device_cnt)\
                   .alias('UNIQUELIST')


class FileSys(object):
    pass

class Arch(object):
    pass
class OS(object):
    pass
class Runlevel(object):
    pass
class NumCPUs(object):
    pass
class Vendor(object):
    pass
class System(object):
    pass
class CPUVendor(object):
    pass
class KernelVersion(object):
    pass
class FormFactor(object):
    pass
class Language(object):
    pass
class TotalList(object):
    pass
class UniqueList(object):
    pass
class SelinuxEnabled(object):
    pass
class SelinuxEnforced(object):
    pass
class SelinuxPolicy(object):
    pass
class MythSystemRole(object):
    pass
class MythRemote(object):
    pass
class MythTheme(object):
    pass

filesys = simple_mapped_counted_view("FILESYSTEMS", file_systems.c.fs_type,
                                     FileSys, desc=True)

archs = simple_mapped_counted_view("ARCH", hosts.c.platform,
                                   Arch, desc=True)

oses = simple_mapped_counted_view("OS", hosts.c.os,
                                  OS, desc=True)

runlevels = simple_mapped_counted_view("RUNLEVEL", hosts.c.default_runlevel, 
                                       Runlevel, desc=True, label='runlevel')

num_cpus = simple_mapped_counted_view("NUM_CPUS", hosts.c.num_cpus, 
                                      NumCPUs, desc=True)

vendors = simple_mapped_counted_view('VENDOR', hosts.c.vendor,
                                     Vendor, desc=True)

systems = simple_mapped_counted_view('SYSTEM', hosts.c.system,
                                     System, desc=True)

cpu_vendors = simple_mapped_counted_view('CPU_VENDOR', hosts.c.cpu_vendor,
                                         CPUVendor, desc=True)

kernel_versions = simple_mapped_counted_view('KERNEL_VERSION', hosts.c.kernel_version,
                                             KernelVersion, desc=True)

formfactors = simple_mapped_counted_view('FORMFACTOR', hosts.c.formfactor,
                                         FormFactor, desc=True)

languages = simple_mapped_counted_view('LANGUAGE', hosts.c.language,
                                       Language, desc=True)

selinux_enabled = simple_mapped_counted_view('SELINUX_ENABLED', hosts.c.selinux_enabled,
                                             SelinuxEnabled, desc=True, label='enabled')

selinux_enforce = simple_mapped_counted_view('SELINUX_ENFORCE', hosts.c.selinux_enforce,
                                             SelinuxEnforced, desc=True, label='enforce')

selinux_policy = simple_mapped_counted_view('SELINUX_POLICY', hosts.c.selinux_policy,
                                            SelinuxPolicy, desc=True, label='policy')

myth_systemroles = simple_mapped_counted_view('MYTH_SYSTEMROLE', hosts.c.myth_systemrole,
                                              MythSystemRole, desc=True)

mythremotes = simple_mapped_counted_view('MYTHREMOTE', hosts.c.mythremote,
                                         MythRemote, desc=True)

myththemes = simple_mapped_counted_view('MYTHTHEME', hosts.c.myththeme,
                                        MythTheme, desc=True)

mapper(TotalList, totallist, order_by=desc(totallist.c.cnt),
       primary_key=[totallist.c.description])

mapper(UniqueList, uniquelist, order_by=desc(uniquelist.c.cnt),
       primary_key=[uniquelist.c.description])


def old_hosts_clause():
    return (hosts.c.last_modified > (date.today() - timedelta(days=36)))
