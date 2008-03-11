from sqlalchemy import *

from hardware.model.model import *

hardware_host_cnt = func.count(func.distinct(host_links.c.host_link_id)).label('cnt')
hardware_by_class = select([host_links.c.device_id.label('id'),
                            computer_logical_devices.c.description,
                            computer_logical_devices.c.bus,
                            computer_logical_devices.c.driver,
                            computer_logical_devices.c.vendor_id,
                            computer_logical_devices.c.device_id,
                            computer_logical_devices.c.subsys_device_id,
                            computer_logical_devices.c.subsys_vendor_id,
                            computer_logical_devices.c.date_added,
                            computer_logical_devices.c.cls,
                            hardware_host_cnt],
                           host_links.c.device_id==computer_logical_devices.c.id)\
                    .group_by(host_links.c.device_id)\
                    .order_by(hardware_host_cnt)\
                    .alias('CLASS')

filetype_cnt = func.count(file_systems.c.fs_type).label('cnt')
filesys = select([file_systems.c.fs_type, filetype_cnt])\
    .group_by(file_systems.c.fs_type)\
    .order_by(filetype_cnt)\
    .alias('FILESYSTEMS')
    
platform_cnt = func.count(hosts.c.platform).label('cnt')
archs = select([hosts.c.platform, platform_cnt])\
    .group_by(hosts.c.platform)\
    .order_by(platform_cnt)\
    .alias("ARCH")

os_cnt = func.count(hosts.c.os).label('cnt')
oses = select([hosts.c.os, os_cnt])\
    .group_by(hosts.c.os)\
    .order_by(os_cnt)\
    .alias('OS')

runlevel_cnt = func.count(hosts.c.default_runlevel).label('cnt')
runlevels = select([hosts.c.default_runlevel.label('runlevel'), runlevel_cnt])\
    .group_by(hosts.c.default_runlevel)\
    .order_by(runlevel_cnt)\
    .alias('RUNLEVEL')

cpu_cnt = func.count(hosts.c.num_cpus).label('cnt')
num_cpus = select([hosts.c.num_cpus, cpu_cnt])\
    .group_by(hosts.c.num_cpus)\
    .order_by(cpu_cnt)\
    .alias('NUM_CPUS')

vendor_cnt = func.count(hosts.c.vendor).label('cnt')
vendors = select([hosts.c.vendor, vendor_cnt])\
    .group_by(hosts.c.vendor)\
    .order_by(vendor_cnt)\
    .alias('VENDOR')

system_cnt = func.count(hosts.c.system).label('cnt')
systems = select([hosts.c.system, system_cnt])\
    .group_by(hosts.c.system)\
    .order_by(system_cnt)\
    .alias('SYSTEM')

cpu_vendor_cnt = func.count(hosts.c.cpu_vendor).label('cnt')
cpu_vendors = select([hosts.c.cpu_vendor, cpu_vendor_cnt])\
    .group_by(hosts.c.cpu_vendor)\
    .order_by(cpu_vendor_cnt)\
    .alias('CPU_VENDOR')

kernel_cnt = func.count(hosts.c.kernel_version).label('cnt')
kernel_versions = select([hosts.c.kernel_version, kernel_cnt])\
    .group_by(hosts.c.kernel_version)\
    .order_by(kernel_cnt)\
    .alias('KERNEL_VERSION')

formfactor_cnt = func.count(hosts.c.formfactor).label('cnt')
formfactors = select([hosts.c.formfactor, formfactor_cnt])\
    .group_by(hosts.c.formfactor)\
    .order_by(formfactor_cnt)\
    .alias('FORMFACTOR')

language_cnt = func.count(hosts.c.language).label('cnt')
languages = select([hosts.c.language, language_cnt])\
    .group_by(hosts.c.language)\
    .order_by(language_cnt)\
    .alias('LANGUAGE')

enabled_cnt = func.count(hosts.c.selinux_enabled).label('cnt')
selinux_enabled = select([hosts.c.selinux_enabled.label('enabled'), enabled_cnt])\
    .group_by(hosts.c.selinux_enabled)\
    .order_by(enabled_cnt)\
    .alias('SELINUX_ENABLED')

enforce_cnt = func.count(hosts.c.selinux_enforce).label('cnt')
selinux_enforce = select([hosts.c.selinux_enforce.label('enforce'), enforce_cnt])\
    .group_by(hosts.c.selinux_enforce)\
    .order_by(enforce_cnt)\
    .alias('SELINUX_ENFORCE')

policy_cnt = func.count(hosts.c.selinux_policy).label('cnt')
selinux_policy = select([hosts.c.selinux_policy.label('policy'), policy_cnt])\
    .group_by(hosts.c.selinux_policy)\
    .order_by(policy_cnt)\
    .alias('SELINUX_POLICY')

mythrole_cnt = func.count(hosts.c.myth_systemrole).label('cnt')
myth_systemroles = select([hosts.c.myth_systemrole, mythrole_cnt])\
    .group_by(hosts.c.myth_systemrole)\
    .order_by(mythrole_cnt)\
    .alias('MYTH_SYSTEMROLE')

remotes_cnt = func.count(hosts.c.mythremote).label('cnt')
mythremotes = select([hosts.c.mythremote, remotes_cnt])\
    .group_by(hosts.c.mythremote)\
    .order_by(remotes_cnt)\
    .alias('MYTHREMOTE')

myththemes_cnt = func.count(hosts.c.myththeme).label('cnt')
myththemes = select([hosts.c.myththeme, myththemes_cnt])\
    .group_by(hosts.c.myththeme)\
    .order_by(myththemes_cnt)\
    .alias('MYTHTHEME')

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

class HardwareByClass(object):
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

mapper(HardwareByClass, hardware_by_class,
       primary_key=[hardware_by_class.c.id])

mapper(OS, oses, order_by=desc(oses.c.cnt),
       primary_key=[oses.c.os])

mapper(Arch, archs, order_by=desc(archs.c.cnt),
       primary_key=[archs.c.platform])

mapper(Runlevel, runlevels, order_by=desc(runlevels.c.cnt),
       primary_key=[runlevels.c.runlevel])

mapper(NumCPUs, num_cpus, order_by=desc(num_cpus.c.cnt),
       primary_key=[num_cpus.c.num_cpus])

mapper(Vendor, vendors, order_by=desc(vendors.c.cnt),
       primary_key=[vendors.c.vendor])

mapper(System, systems, order_by=desc(systems.c.cnt),
       primary_key=[systems.c.system])

mapper(CPUVendor, cpu_vendors, order_by=desc(cpu_vendors.c.cnt),
       primary_key=[cpu_vendors.c.cpu_vendor])

mapper(KernelVersion, kernel_versions, order_by=desc(kernel_versions.c.cnt),
       primary_key=[kernel_versions.c.kernel_version])

mapper(FormFactor, formfactors, order_by=desc(formfactors.c.cnt),
       primary_key=[formfactors.c.formfactor])

mapper(Language, languages, order_by=desc(languages.c.cnt),
       primary_key=[languages.c.language])

mapper(SelinuxEnabled, selinux_enabled, order_by=desc(selinux_enabled.c.cnt),
       primary_key=[selinux_enabled.c.enabled])

mapper(SelinuxEnforced, selinux_enforce, order_by=desc(selinux_enforce.c.cnt),
       primary_key=[selinux_enforce.c.enforce])

mapper(SelinuxPolicy, selinux_policy, order_by=desc(selinux_policy.c.cnt),
       primary_key=[selinux_policy.c.policy])

mapper(MythSystemRole, myth_systemroles, order_by=desc(myth_systemroles.c.cnt),
       primary_key=[myth_systemroles.c.myth_systemrole])

mapper(MythTheme, myththemes, order_by=desc(myththemes.c.cnt),
       primary_key=[myththemes.c.myththeme])

mapper(MythRemote, mythremotes, order_by=desc(mythremotes.c.cnt),
       primary_key=[mythremotes.c.mythremote])

mapper(TotalList, totallist, order_by=desc(totallist.c.cnt),
       primary_key=[totallist.c.description])

mapper(UniqueList, uniquelist, order_by=desc(uniquelist.c.cnt),
       primary_key=[uniquelist.c.description])

mapper(FileSys, filesys, order_by=desc(filesys.c.cnt),
       primary_key=[filesys.c.fs_type])


def old_hosts_clause():
    return (hosts.c.last_modified > (date.today() - timedelta(days=36)))
