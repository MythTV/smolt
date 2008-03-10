from datetime import datetime
from sqlalchemy import *
from sqlalchemy.orm import *
from turbogears.database import metadata, session
from sqlalchemy.ext.assignmapper import assign_mapper
from turbogears import identity
from datetime import timedelta, date, datetime


#ctx = session.context


computer_logical_devices = \
       Table('device', metadata,
             Column("id", INT, autoincrement=True,
                    nullable=False, primary_key=True),
             Column("description", VARCHAR(128),
                    nullable=False),
             Column("bus", TEXT),
             Column("driver", TEXT),
             Column("class", VARCHAR(24),
                    ForeignKey("classes.cls"),
                    key="cls"),
             Column("date_added", DATETIME),
             Column("device_id", INT),
             Column("vendor_id", INT),
             Column("subsys_device_id", INT),
             Column("subsys_vendor_id", INT))

host_links = Table('host_links', metadata,
                   Column("id", INT,
                          autoincrement=True,
                          nullable=False,
                          primary_key=True),
                   Column('host_link_id', INT,
                          ForeignKey("host.id"),
                          nullable=False),
                   Column("device_id", INT,
                          ForeignKey("device.id")),
                   Column("rating", INT))

hosts = Table('host', metadata,
              Column("id", INT,
                     autoincrement=True,
                     nullable=False,
                     primary_key=True),
              Column('uuid', VARCHAR(36),
                     nullable=False,
                     unique=True),
              Column('pub_uuid', VARCHAR(40),
                     nullable=False,
                     unique=True),
              Column('os', TEXT),
              Column('platform', TEXT),
              Column('bogomips', DECIMAL),
              Column('system_memory', INT),
              Column('system_swap', INT),
              Column('vendor', TEXT),
              Column('system', TEXT),
              Column('cpu_vendor', TEXT),
              Column('cpu_model', TEXT),
              Column('num_cpus', INT),
              Column('cpu_speed', DECIMAL),
              Column('language', TEXT),
              Column('default_runlevel', INT),
              Column('kernel_version', TEXT),
              Column('formfactor', TEXT),
              Column('last_modified', DATETIME,
                     default=0, nullable=False),
              Column('rating', INT, nullable=False, default=0),
              Column('selinux_enabled', BOOLEAN, nullable=False),
              Column('selinux_policy', TEXT),
              Column('selinux_enforce', TEXT),
              Column('myth_systemrole', TEXT),
              Column('mythremote', TEXT),
              Column('myththeme', TEXT))

fas_links = Table('fas_link', metadata,
                  Column("id", INT, autoincrement=True,
                         nullable=False, primary_key=True),
                  Column('uuid', VARCHAR(36),
                         ForeignKey("host.uuid"),
                         nullable=False),
                  Column("user_name", VARCHAR(255),
                         nullable=False))

hardware_classes = Table('classes', metadata,
                         Column("class", VARCHAR(24),
                                nullable=False,
                                primary_key=True, key="cls"),
                         Column("description", TEXT,
                                key="class_description"))

file_systems = Table('file_systems', metadata,
                     Column('id', INT, autoincrement=True,
                            nullable=False, primary_key=True),
                     Column('host_id', INT,
                            ForeignKey("host.id")),
                     Column('mnt_pnt', TEXT),
                     Column('fs_type', TEXT),
                     Column('f_favail', INT),
                     Column('f_bsize', INT),
                     Column('f_frsize', INT),
                     Column('f_blocks', INT),
                     Column('f_bfree', INT),
                     Column('f_bavail', INT),
                     Column('f_files', INT),
                     Column('f_ffree', INT),
                     Column('f_fssize', INT))

filesys = Table("FILESYSTEMS", metadata,
                         Column("fs_type", TEXT,
                                primary_key=True),
                         Column("cnt", INT))

hardware_by_class = Table("CLASS", metadata,
                          Column('device_id', VARCHAR(16),
                                 primary_key=True),
                          Column('description', VARCHAR(128)),
                          Column('bus', TEXT),
                          Column("driver", TEXT),
                          Column("vendor_id", INT),
                          Column("subsys_vendor_id", INT),
                          Column("subsys_device_id", INT),
                          Column("date_added", DATETIME),
                          Column("cnt", INT, key='count'),
                          Column("class", TEXT, key="cls"))

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
runlevels = select([hosts.c.default_runlevel, runlevel_cnt])\
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

l_cnt = func.count(hosts.c.language).label('cnt')
languages = select([hosts.c.language, l_cnt])\
    .group_by(hosts.c.language)\
    .order_by(l_cnt)\
    .alias('LANGUAGE')

enabled_cnt = func.count(hosts.c.selinux_enabled).label('cnt')
selinux_enabled = select([hosts.c.selinux_enabled, enabled_cnt])\
    .group_by(hosts.c.selinux_enabled)\
    .order_by(enabled_cnt)\
    .alias('SELINUX_ENABLED')

enforce_cnt = func.count(hosts.c.selinux_enforce).label('cnt')
selinux_enforce = select([hosts.c.selinux_enforce, enforce_cnt])\
    .group_by(hosts.c.selinux_enforce)\
    .order_by(enforce_cnt)\
    .alias('SELINUX_ENFORCE')

policy_cnt = func.count(hosts.c.selinux_policy).label('cnt')
selinux_policy = select([hosts.c.selinux_policy, policy_cnt])\
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

totallist = Table("TOTALLIST", metadata,
                  Column('description', TEXT,
                         primary_key=True),
                  Column('cnt', INT, key="count"))

uniquelist = Table("UNIQUELIST", metadata,
                   Column('description', TEXT,
                          primary_key=True),
                   Column('cnt', INT, key='count'))

class Host(object):
    def __init__(self, selinux_enabled=False,
                 rating=0, last_modified=datetime.today()):
        self.selinux_enabled = selinux_enabled
        self.rating = rating
        self.last_modified = last_modified

class ComputerLogicalDevice(object):
    pass

class HostLink(object):
    def __init__(self, rating=0):
        self.rating = rating

class FasLink(object):
    def __init__(self, uuid, user_name):
        self.uuid = uuid
        self.user_name = user_name

class HardwareClass(object):
    def _set_cls(self, cls):
        if cls is None:
            cls = "NONE"
        self._cls = cls
    def _get_cls(self):
        return self._cls
    pass
    cls = property(_get_cls, _set_cls)

class FileSystem(object):
    pass

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
class Foo(object):
    """Bar"""
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

mapper(Foo, hosts,
       properties = {'clds': relation(ComputerLogicalDevice, \
                                      secondary=host_links)})

mapper(Host, hosts,
       properties=dict(_devices=relation(HostLink,
                                         cascade="all,delete-orphan",
                                         backref=backref('host'),
                                         lazy=None),
                      devices=relation(HostLink, cascade='all,delete-orphan'),
                      fas_account=relation(FasLink, uselist=False),
                      file_systems=relation(FileSystem,
                                            backref='host')))

mapper(ComputerLogicalDevice,
       computer_logical_devices,
       properties = {"_host_links": relation(HostLink,
                                            cascade="all,delete-orphan",
                                            backref=backref('device'),
                                            lazy=None),
                     "host_links": relation(HostLink,
                                            cascade="all,delete-orphan")})

mapper(HostLink, host_links)

mapper(FasLink, fas_links, properties = {'hosts': relation(Host),
                                         'uuid': fas_links.c.uuid})

mapper(HardwareClass,
       hardware_classes,
       properties = {'devices': relation(ComputerLogicalDevice,
                                         cascade="all,delete-orphan",
                                         backref=backref('hardware_class'),
                                         lazy=None),
                     '_cls': hardware_classes.c.cls,
                     'cls': synonym('_cls')})
mapper(FileSystem,
       file_systems)
mapper(FileSys, filesys, order_by=desc(filesys.c.cnt))
mapper(HardwareByClass, hardware_by_class)
mapper(OS, oses, order_by=desc(oses.c.cnt),
       primary_key=[oses.c.os])

mapper(Arch, archs, order_by=desc(archs.c.cnt),
       primary_key=[archs.c.platform])

mapper(Runlevel, runlevels, order_by=desc(runlevels.c.cnt),
       primary_key=[runlevels.c.default_runlevel])

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
       primary_key=[selinux_enabled.c.selinux_enabled])

mapper(SelinuxEnforced, selinux_enforce, order_by=desc(selinux_enforce.c.cnt),
       primary_key=[selinux_enforce.c.selinux_enforce])

mapper(SelinuxPolicy, selinux_policy, order_by=desc(selinux_policy.c.cnt),
       primary_key=[selinux_policy.c.selinux_policy])

mapper(MythSystemRole, myth_systemroles, order_by=desc(myth_systemroles.c.cnt),
       primary_key=[myth_systemroles.c.myth_systemrole])

mapper(MythTheme, myththemes, order_by=desc(myththemes.c.cnt),
       primary_key=[myththemes.c.myththeme])

mapper(MythRemote, mythremotes, order_by=desc(mythremotes.c.cnt),
       primary_key=[mythremotes.c.mythremote])

mapper(TotalList, totallist, order_by=desc(totallist.c.count))
mapper(UniqueList, uniquelist, order_by=desc(uniquelist.c.count))

def old_hosts_clause():
    return (hosts.c.last_modified > (date.today() - timedelta(days=36)))
