# -*- coding: utf-8 -*-
from datetime import datetime
from sqlalchemy import *
from sqlalchemy.orm import *
from turbogears.database import metadata, session
#from sqlalchemy.ext.assignmapper import assign_mapper
from turbogears import identity
from datetime import timedelta, date, datetime
from turbogears.database import mapper




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
            Column('selinux_enabled', INT, nullable=False),
            Column('selinux_policy', TEXT),
            Column('selinux_enforce', TEXT),
            Column('cpu_stepping', INT, default=None),
            Column('cpu_family', INT, default=None),
            Column('cpu_model_num', INT, default=None),
            Column('myth_role', TEXT),
            Column('myth_remote', TEXT),
            Column('myth_theme', TEXT),
            Column('myth_plugins',TEXT),
            Column('myth_tuner', INT))


hosts_archive = Table('host_archive', metadata,
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
            Column('selinux_enabled', INT, nullable=False),
            Column('selinux_policy', TEXT),
            Column('selinux_enforce', TEXT),
            Column('cpu_stepping', INT, default=None),
            Column('cpu_family', INT, default=None),
            Column('cpu_model_num', INT, default=None),
            Column('myth_role', TEXT),
            Column('myth_remote', TEXT),
            Column('myth_theme', TEXT),
            Column('myth_plugins',TEXT),
            Column('myth_tuner', INT))



