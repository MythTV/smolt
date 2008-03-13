from sqlalchemy import *

from hardware.model.model import *

def column_cnt(column):
    '''This is a counted column.  A convenience function'''
    return func.count(column).label('cnt')

def column_cnt_d(column):
    '''The same as column_cnt, but distinct'''
    return func.count(func.distinct(column)).label('cnt')

def counted_view(name, columns, group_by, restrictions=None, desc=False, distinct=False):
    '''Generates a satistical counted view of some table or simple join 
    for some group of columns.
    
    This function is a bit low level, and you probably want the
    simple version of this: simple_mapped_counted_view
    
    params:
        name is the name of the view
        columns is an iterable with the columns desired
            - multiple tables' columns may be used here, for simple joins
            - what is in group_by should not be included here
        group_by the object to group on, such that it is counted
        restrictions are sqlalchemy where constraints
        desc is a boolean whether you want it in ascending, descending or condescending order
    ''' 
    cnt_f = column_cnt_d if distinct else column_cnt
    cnt_obj = cnt_f(group_by)
    s = select(columns + [group_by, cnt_obj], restrictions).group_by(group_by)
    if desc:
        cnt_obj = cnt_obj.desc()
    return s.order_by(cnt_obj).alias(name)

def simple_counted_view(name, column, desc=False, label=None, distinct=False):
    '''Generates a counted view on a single column'''
    if label:
        column = column.label(label)
    return counted_view(name, [column], column, desc=desc, distinct=distinct)

#This creates one ugly sideeffect, but I couldn't think of a better way off hand
#that doesn't require a sever language adjustment :p -ynemoy
def mapped_counted_view(name, map_obj, columns, group_by, restrictions=None, desc=False, distinct=False):
    sel = counted_view(name, columns, group_by, restrictions, desc, distinct)
    p_key = getattr(sel.c, group_by.name)
    mapper(map_obj, sel, primary_key=[p_key])
    return sel
    
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
    sel = simple_counted_view(name, column, desc, label)
    p_key = getattr(sel.c, label) if label else getattr(sel.c, column.name)
    mapper(map_obj, sel, primary_key=[p_key])
    return sel
    

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

#this references hosts just as an example for now, this will become necessary later
filesys = mapped_counted_view("FILESYSTEMS", FileSys, [],
                              file_systems.c.fs_type, hosts.c.id==file_systems.c.host_id, desc=True)

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

totallist = mapped_counted_view('TOTALLIST', TotalList,
                                [computer_logical_devices.c.description],
                                host_links.c.device_id,
                                host_links.c.device_id==computer_logical_devices.c.id,
                                desc=True)

uniquelist = mapped_counted_view('UNIQUELIST', UniqueList,
                                [computer_logical_devices.c.description],
                                host_links.c.device_id,
                                host_links.c.device_id==computer_logical_devices.c.id,
                                desc=True, distinct=True)
 


def old_hosts_clause():
    return (hosts.c.last_modified > (date.today() - timedelta(days=36)))

def old_hosts_table():
    return select([hosts], old_hosts_clause()).alias('old_hosts')
