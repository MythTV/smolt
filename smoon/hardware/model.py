from datetime import datetime
from sqlalchemy import *
from turbogears.database import metadata, session
from sqlalchemy.ext.assignmapper import assign_mapper
from turbogears import identity

def assign(*args, **kw):
    """Map tables to objects with knowledge about the session context."""
    return assign_mapper(session.context, *args, **kw)


computer_logical_devices = Table('device', metadata, 
                                 Column("id", INT, autoincrement=True,
                                        nullable=False, primary_key=True),
                                 Column("description", VARCHAR(128),
                                        nullable=False),
                                 Column("bus", TEXT),
                                 Column("driver", TEXT),
                                 Column("class", TEXT),
                                 Column("date_added", DATETIME),
                                 Column("device_id", VARCHAR(16)),
                                 Column("vendor_id", INT),
                                 Column("subsys_device_id", INT),
                                 Column("subsys_vendor_id", INT))

host_links = Table('host_links', metadata, 
                   Column("id", INT, autoincrement=True, nullable=False, primary_key=True),
                   Column('host_link_id', INT, ForeignKey("host.id"),
                          nullable=False),
                   Column("device_id", INT, ForeignKey("device.device_id")),
                   Column("rating", INT))

hosts = Table('host', metadata,
              Column("id", INT, autoincrement=True, nullable=False, primary_key=True),
              Column('u_u_id', VARCHAR(36), nullable=False, unique=True),
              Column('o_s', TEXT),
              Column('platform', TEXT),
              Column('bogomips', DECIMAL),
              Column('system_memory', INT),
              Column('system_swap', INT),
              Column('vendor', TEXT),
              Column('system', TEXT),
              Column('cpu_vendor', TEXT),
              Column('cpu_model', TEXT),
              Column('num_cp_us', INT),
              Column('cpu_speed', DECIMAL),
              Column('language', TEXT),
              Column('default_runlevel', INT),
              Column('kernel_version', TEXT),
              Column('formfactor', TEXT),
              Column('last_modified', DATETIME, default=0, nullable=False),
              Column('rating', INT, nullable=False, default=0),
              Column('selinux_enabled', BOOLEAN, nullable=False),
              Column('selinux_enforce', TEXT))

fas_links = Table('fas_link', metadata,
                  Column("id", INT, autoincrement=True, nullable=False,
                         primary_key=True),
                  Column('u_u_id', VARCHAR(36), ForeignKey("host.u_u_id"),
                         nullable=False),
                  Column("user_name", VARCHAR(255), nullable=False))


class Host(object):
    pass

class ComputerLogicalDevice(object):
    pass

class HostLinks(object):
    pass

class FasLink(object):
    pass

assign(Host, hosts, properties = {
                      'uuid' : hosts.c.u_u_id,
                      'os': hosts.c.o_s,
                      'num_cpus': hosts.c.num_cp_us,
                      'devices': relation(HostLinks),
                      'fas_account': relation(FasLink, uselist=False)})
assign(ComputerLogicalDevice, computer_logical_devices)
assign(HostLinks, host_links, properties = {
                                'host': relation(Host, uselist=False),
                                'device': relation(ComputerLogicalDevice,
                                                   uselist=False)})
assign(FasLink, fas_links, properties = {'hosts': relation(Host)})
