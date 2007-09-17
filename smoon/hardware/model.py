from datetime import datetime

from sqlalchemy import *
from sqlalchemy.ext.assignmapper import assign_mapper
from turbogears import identity
from mx import DateTime

from sahelper import ctx, metadata


computer_logical_devices = Table('device', metadata, 
                                 Column("id", Integer, autoincrement=True,
                                        nullable=False, primary_key=True),
                                 Column("description", String(128),
                                        nullable=False),
                                 Column("bus", String),
                                 Column("driver", String),
                                 Column("class", String(24),
                                        ForeignKey("classes.cls"),
                                        key="cls"),
                                 Column("date_added", DateTime),
                                 Column("device_id", String(16)),
                                 Column("vendor_id", Integer),
                                 Column("subsys_device_id", Integer),
                                 Column("subsys_vendor_id", Integer))

human_logical_device = Table('subsystem', metadata,
                             Column('name', String(20),
                                    nullable=False, primary_key=True),
                             Column('description', String))

hld_cld_links = Table('hld_cld_link', metadata,
                      Column('id', Integer, autoincrement=True,
                             nullable=False, primary_key=True),
                      Column('hld', String(30), ForeignKey('subsystem.name')),
                      Column('cld', Integer, ForeignKey('device.id')))

hld_host_links = Table('hld_host_link', metadata,
                       Column('id', Integer, autoincrement=True,
                              nullable=False, primary_key=True),
                       Column('hld', String(30), ForeignKey('subsystem.name')),
                       Column('host_id', Integer, ForeignKey('host.id')),
                       Column('rating', Integer))

host_links = Table('host_links', metadata, 
                   Column("id", Integer, autoincrement=True, nullable=False, primary_key=True),
                   Column('host_link_id', Integer, ForeignKey("host.id"),
                          nullable=False),
                   Column("device_id", Integer, ForeignKey("device.id")),
                   Column("rating", Boolean))

hosts = Table('host', metadata,
              Column("id", Integer, autoincrement=True, nullable=False, primary_key=True),
              Column('u_u_id', String(36), nullable=False, unique=True),
              Column('o_s', String),
              Column('platform', String),
              Column('bogomips', Numeric),
              Column('system_memory', Integer),
              Column('system_swap', Integer),
              Column('vendor', String),
              Column('system', String),
              Column('cpu_vendor', String),
              Column('cpu_model', String),
              Column('num_cp_us', Integer),
              Column('cpu_speed', Numeric),
              Column('language', String),
              Column('default_runlevel', Integer),
              Column('kernel_version', String),
              Column('formfactor', String),
              Column('last_modified', DateTime, default=0, nullable=False),
              Column('rating', Integer, nullable=False, default=0),
              Column('selinux_enabled', Boolean, nullable=False),
              Column('selinux_enforce', String))

fas_links = Table('fas_link', metadata,
                  Column("id", Integer, autoincrement=True, nullable=False,
                         primary_key=True),
                  Column('u_u_id', String(36), ForeignKey("host.u_u_id"),
                         nullable=False),
                  Column("user_name", String(255), nullable=False))

hardware_classes = Table('classes', metadata,
                         Column("class", String(24), nullable=False, primary_key=True, key="cls"),
                         Column("description", String, key="class_description"))

hardware_by_class = Table("CLASS", metadata,
                          Column('device_id', String(16), primary_key=True),
                          Column('description', String(128)),
                          Column('bus', String),
                          Column("driver", String),
                          Column("vendor_id", Integer),
                          Column("subsys_vendor_id", Integer),
                          Column("subsys_device_id", Integer),
                          Column("date_added", DateTime),
                          Column("cnt", Integer, key='count'),
                          Column("class", String, key="cls"))

archs = Table("ARCH", metadata,
                  Column("platform", String, primary_key=True),
                  Column("cnt", Integer))
oses = Table("OS", metadata,
                  Column("o_s", String, primary_key=True, key="os"),
                  Column("cnt", Integer))
runlevels = Table("RUNLEVEL", metadata,
                      Column("default_runlevel", Integer, primary_key=True, key="runlevel"),
                      Column("cnt", Integer))
num_cpus = Table("NUM_CPUS", metadata,
                     Column("num_cp_us", Integer, primary_key=True, key="num_cpus"),
                     Column("cnt", Integer))
vendors = Table("VENDOR", metadata,
                    Column("vendor", String, primary_key=True),
                    Column("cnt", Integer))
systems = Table("SYSTEM", metadata,
                    Column("system", String, primary_key=True),
                    Column("cnt", Integer))
cpu_vendors = Table("CPU_VENDOR", metadata,
                    Column("cpu_vendor", String, primary_key=True),
                    Column("cnt", Integer))
kernel_versions = Table("KERNEL_VERSION", metadata,
                            Column("kernel_version", String, primary_key=True),
                            Column("cnt", Integer))
formfactors = Table("FORMFACTOR", metadata,
                         Column("formfactor", String, primary_key=True),
                         Column("cnt", Integer))
languages = Table("LANGUAGE", metadata,
                      Column('language', String, primary_key=True),
                      Column('cnt', Integer))

totallist = Table("TOTALLIST", metadata,
                  Column('description', String, primary_key=True),
                  Column('cnt', Integer, key="count"))

uniquelist = Table("UNIQUELIST", metadata,
                   Column('description', String, primary_key=True),
                   Column('cnt', Integer, key='count'))

class Host(object):
    def __init__(self, selinux_enabled=False, rating=0, last_modified=DateTime.now()):
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

mapper(Foo, hosts,
       properties = {'clds': relation(ComputerLogicalDevice, secondary=host_links)})

mapper(Host, hosts,
       properties = {
          'uuid' : hosts.c.u_u_id,
          'os': hosts.c.o_s,
          'num_cpus': hosts.c.num_cp_us,
          '_devices': relation(HostLink,
                               cascade="all,delete-orphan",
                               backref=backref('host'),
                               lazy=None),
          'devices': relation(HostLink, cascade='all,delete-orphan'),
          'fas_account': relation(FasLink, uselist=False)})

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
                                         'uuid': fas_links.c.u_u_id})

mapper(HardwareClass,
       hardware_classes,
       properties = {'devices': relation(ComputerLogicalDevice,
                                         cascade="all,delete-orphan",
                                         backref=backref('hardware_class'),
                                         lazy=None),
                     '_cls': hardware_classes.c.cls,
                     'cls': synonym('_cls')})

mapper(HardwareByClass, hardware_by_class)
mapper(OS, oses, order_by=desc(oses.c.cnt))
mapper(Arch, archs, order_by=desc(archs.c.cnt))
mapper(Runlevel, runlevels, order_by=desc(runlevels.c.cnt))
mapper(NumCPUs, num_cpus, order_by=desc(num_cpus.c.cnt))
mapper(Vendor, vendors, order_by=desc(vendors.c.cnt))
mapper(System, systems, order_by=desc(systems.c.cnt))
mapper(CPUVendor, cpu_vendors, order_by=desc(cpu_vendors.c.cnt))
mapper(KernelVersion, kernel_versions, order_by=desc(kernel_versions.c.cnt))
mapper(FormFactor, formfactors, order_by=desc(formfactors.c.cnt))
mapper(Language, languages, order_by=desc(languages.c.cnt))
mapper(TotalList, totallist, order_by=desc(totallist.c.count))
mapper(UniqueList, uniquelist, order_by=desc(uniquelist.c.count))

