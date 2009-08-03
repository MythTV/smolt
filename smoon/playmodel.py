# smolt - Fedora hardware profiler
#
# Copyright (C) 2009 Sebastian Pipping <sebastian@pipping.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301, USA.

import logging
from sqlalchemy import Table, Column, Integer, BOOLEAN, SmallInteger, CHAR, ForeignKey, UniqueConstraint
from sqlalchemy.orm import mapper, relation


# Context dependent metadata creation
import sys
if 'turbogears' in sys.modules:
    logging.debug('Turbogears context')
    from turbogears.database import metadata
else:
    logging.debug('Plain SQL alchemy context')
    from sqlalchemy import MetaData
    metadata = MetaData()


_GENTOO_KEYWORD_STATUS_EMPTY, \
    _GENTOO_KEYWORD_STATUS_TILDE_ARCH, \
    _GENTOO_KEYWORD_STATUS_DOUBLE_ASTERISK = range(0, 3)

_keyword_status_map = {
    '':_GENTOO_KEYWORD_STATUS_EMPTY,
    '~arch':_GENTOO_KEYWORD_STATUS_TILDE_ARCH,
    '**':_GENTOO_KEYWORD_STATUS_DOUBLE_ASTERISK,
}

def keyword_status_code(keyword_status):
    try:
        return _keyword_status_map[keyword_status]
    except KeyError:
        return _GENTOO_KEYWORD_STATUS_EMPTY


# ================================================================
# _POOL_TABLE_TEMPLATE
# ================================================================
_POOL_TABLE_TEMPLATE = """
%(table_var_name)s = Table('%(table_name)s', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', %(col_type)s, unique=True),
)

class %(class_name)s(object):
    def __init__(self, name):
        self.name = name

mapper(%(class_name)s, %(table_var_name)s)
"""


# ================================================================
# _SCALAR_REL_TABLE_TEMPLATE
# ================================================================
_SCALAR_REL_TABLE_TEMPLATE = """
%(table_var_name)s = Table('%(table_name)s', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('machine_id', Integer, primary_key=True),
    Column('%(foreign_key_column)s', Integer, ForeignKey('%(foreign_key_table)s.id')),
)

class %(class_name)s(object):
    def __init__(self, machine_id, %(foreign_key_column)s):
        self.machine_id = machine_id
        self.%(foreign_key_column)s = %(foreign_key_column)s

mapper(%(class_name)s, %(table_var_name)s,
    properties={
        '%(relation_name)s':relation(%(foreign_key_class)s),
    }
)
"""


# ================================================================
# _VECTOR_REL_TABLE_TEMPLATE
# ================================================================
_VECTOR_REL_TABLE_TEMPLATE = """
%(table_var_name)s = Table('%(table_name)s', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('machine_id', Integer),
    Column('%(foreign_key_column)s', Integer, ForeignKey('%(foreign_key_table)s.id')),
    UniqueConstraint('machine_id', '%(foreign_key_column)s'),
)

class %(class_name)s(object):
    def __init__(self, machine_id, %(foreign_key_column)s):
        self.machine_id = machine_id
        self.%(foreign_key_column)s = %(foreign_key_column)s

mapper(%(class_name)s, %(table_var_name)s,
    properties={
        '%(relation_name)s':relation(%(foreign_key_class)s),
    }
)
"""


_pool_table_jobs = [
    {'thing':'atom', 'col_type':'CHAR(255)'},
    {'thing':'call_flag', 'col_type':'CHAR(255)'},
    {'thing':'call_flag_class', 'col_type':'CHAR(255)'},
    {'thing':'chost', 'col_type':'CHAR(255)'},
    {'thing':'feature', 'col_type':'CHAR(127)'},
    {'thing':'keyword', 'col_type':'CHAR(127)'},
    {'thing':'mirror', 'col_type':'CHAR(255)'},
    {'thing':'package', 'col_type':'CHAR(255)'},
    {'thing':'repository', 'col_type':'CHAR(127)'},
    {'thing':'slot', 'col_type':'CHAR(127)'},
    {'thing':'system_profile', 'col_type':'CHAR(255)'},
    {'thing':'use_flag', 'col_type':'CHAR(127)'},
    {'thing':'version', 'col_type':'CHAR(127)'},
]


_rel_table_jobs = [
    {'thing':'arch', 'foreign':'keyword', 'vector_flag':False},
    {'thing':'chost', 'foreign':'chost', 'vector_flag':False},
    {'thing':'sync_mirror', 'foreign':'mirror', 'vector_flag':False},
    {'thing':'distfiles_mirror', 'foreign':'mirror', 'vector_flag':True},
    {'thing':'feature', 'foreign':'feature', 'vector_flag':True},
    {'thing':'global_use_flag', 'foreign':'use_flag', 'vector_flag':True},
    {'thing':'overlay', 'foreign':'repository', 'vector_flag':True},
    {'thing':'system_profile', 'foreign':'system_profile', 'vector_flag':False},
]


def dump_gentoo_python_code(code):
    return  # TODO
    print '============================================='
    for i, v in enumerate(code.split('\n')):
        print '% 5d  %s' % (i + 1, v)
    print '============================================='


def numerus(vector_flag):
    if vector_flag:
        return 's'
    else:
        return ''

def _pool_table_name(middle):
    return 'gentoo_%s_pool' % middle

def _pool_table_instance(middle, vector_flag=False):
    return '_gentoo_%s%s_pool_table' % (middle, numerus(vector_flag))

def pool_class_name(middle, vector_flag=False):
    return 'Gentoo%sString' % middle.title().replace('_', '')

def _rel_table_name(middle, vector_flag=False):
    return 'gentoo_%s%s_rel' % (middle, numerus(vector_flag))

def _rel_table_instance(middle, vector_flag=False):
    return '_gentoo_%s%s_rel_table' % (middle, numerus(vector_flag))

def rel_class_name(middle):
    return 'Gentoo%sRel' % middle.title().replace('_', '')

def _foreign_key_column(middle):
    return '%s_id' % middle


# Create pool tables
for job in _pool_table_jobs:
    thing = job['thing']
    col_type = job['col_type']
    details = {
        'table_name':_pool_table_name(thing),
        'table_var_name':_pool_table_instance(thing),
        'class_name':pool_class_name(thing),
        'col_type':col_type,
    }
    logging.debug('Generating table "%(table_name)s" and related class "%(class_name)s"...' % details)
    program = _POOL_TABLE_TEMPLATE % details
    dump_gentoo_python_code(program)
    exec(program)


# Create relation tables
for job in _rel_table_jobs:
    thing = job['thing']
    foreign = job['foreign']
    vector_flag = job['vector_flag']
    details = {
        'table_name':_rel_table_name(thing, vector_flag),
        'table_var_name':_rel_table_instance(thing, vector_flag),
        'class_name':rel_class_name(thing),
        'foreign_key_table':_pool_table_name(foreign),
        'foreign_key_column':_foreign_key_column(foreign),
        'foreign_key_class':pool_class_name(foreign, vector_flag),
        'relation_name':foreign,
    }
    logging.debug('Generating table "%(table_name)s" and related class "%(class_name)s"...' % details)
    if vector_flag:
        program = _VECTOR_REL_TABLE_TEMPLATE % details
    else:
        program = _SCALAR_REL_TABLE_TEMPLATE % details
    dump_gentoo_python_code(program)
    exec(program)


_gentoo_installed_packages_rel = Table('gentoo_installed_packages_rel', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('machine_id', Integer),
    Column('package_id', Integer, ForeignKey('%s.id' % 'gentoo_package_pool')),
    Column('slot_id', Integer, ForeignKey('%s.id' % 'gentoo_slot_pool')),
    UniqueConstraint('machine_id', 'package_id', 'slot_id'),
)

class GentooInstalledPackagesRel(object):
    def __init__(self, machine_id, package_id, slot_id):
        self.machine_id = machine_id
        self.package_id = package_id
        self.slot_id = slot_id


_gentoo_installed_package_properties_rel_table = Table('gentoo_installed_package_properties_rel', metadata,
    Column('install_id', Integer, ForeignKey('%s.id' % 'gentoo_installed_packages_rel'), primary_key=True, autoincrement=False),
    Column('version_id', Integer, ForeignKey('%s.id' % 'gentoo_version_pool')),
    Column('keyword_status', Integer),  # Could be MSEnum, choosing Integer for flexibility
    Column('masked', BOOLEAN),
    Column('unmasked', BOOLEAN),
    Column('world', BOOLEAN),
    Column('repository_id', Integer, ForeignKey('%s.id' % 'gentoo_repository_pool')),
)

class GentooInstalledPackagePropertiesRel(object):
    def __init__(self, install_id, version_id, keyword_status, masked, unmasked, world, repository_id):
        self.install_id = install_id
        self.version_id = version_id
        self.keyword_status = keyword_status
        self.masked = masked
        self.unmasked = unmasked
        self.world = world
        self.repository_id = repository_id

mapper(GentooInstalledPackagePropertiesRel, _gentoo_installed_package_properties_rel_table,
    properties={
        'install':relation(GentooInstalledPackagesRel),
    }
)


_gentoo_installed_package_use_flag_rel_table = Table('gentoo_installed_package_use_flag_rel', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('install_id', Integer, ForeignKey('%s.id' % 'gentoo_installed_packages_rel')),
    Column('use_flag_id', Integer, ForeignKey('%s.id' % 'gentoo_use_flag_pool')),
    UniqueConstraint('install_id', 'use_flag_id'),
)

class GentooInstalledPackageUseFlagRel(object):
    def __init__(self, install_id, use_flag_id):
        self.install_id = install_id
        self.use_flag_id = use_flag_id

mapper(GentooInstalledPackageUseFlagRel, _gentoo_installed_package_use_flag_rel_table,
    properties={
        'install':relation(GentooInstalledPackagesRel),
    }
)


mapper(GentooInstalledPackagesRel, _gentoo_installed_packages_rel,
    properties={
        'package':relation(GentooPackageString),
        'slot':relation(GentooSlotString),
        'properties':relation(GentooInstalledPackagePropertiesRel, cascade="all, delete, delete-orphan"),
        'use_flags':relation(GentooInstalledPackageUseFlagRel, cascade="all, delete, delete-orphan"),
    }
)


_gentoo_package_mask_rel_table = Table('gentoo_package_mask_rel', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('machine_id', Integer),
    Column('package_id', Integer, ForeignKey('%s.id' % 'gentoo_package_pool')),
    Column('atom_id', Integer, ForeignKey('%s.id' % 'gentoo_atom_pool')),
    UniqueConstraint('machine_id', 'atom_id'),
)

class GentooPackageMaskRel(object):
    def __init__(self, machine_id, package_id, atom_id):
        self.machine_id = machine_id
        self.package_id = package_id
        self.atom_id = atom_id

mapper(GentooPackageMaskRel, _gentoo_package_mask_rel_table,
    properties={
        'package':relation(GentooPackageString),
        'atom':relation(GentooAtomString),
    }
)


_gentoo_accept_keywords_rel_table = Table('gentoo_accept_keyword_rel', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('machine_id', Integer),
    Column('keyword_id', Integer, ForeignKey('%s.id' % 'gentoo_keyword_pool')),
    Column('stable', SmallInteger),  # Not BOOLEAN here as that denies using func.sum
    UniqueConstraint('machine_id', 'keyword_id'),
)

class GentooAcceptKeywordRel(object):
    def __init__(self, machine_id, keyword_id, stable):
        self.machine_id = machine_id
        self.keyword_id = keyword_id
        self.stable = stable

mapper(GentooAcceptKeywordRel, _gentoo_accept_keywords_rel_table,
    properties={
        'keyword':relation(GentooKeywordString),
    }
)


_gentoo_call_flag_rel_table = Table('gentoo_call_flag_rel', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('machine_id', Integer),
    Column('call_flag_class_id', Integer, ForeignKey('%s.id' % 'gentoo_call_flag_class_pool')),
    Column('call_flag_id', Integer, ForeignKey('%s.id' % 'gentoo_call_flag_pool')),
    Column('position', SmallInteger),
    UniqueConstraint('machine_id', 'call_flag_class_id', 'call_flag_id', 'position'),
)

class GentooCallFlagRel(object):
    def __init__(self, machine_id, call_flag_class_id, call_flag_id, position):
        self.machine_id = machine_id
        self.call_flag_class_id = call_flag_class_id
        self.call_flag_id = call_flag_id
        self.position = position

mapper(GentooCallFlagRel, _gentoo_call_flag_rel_table,
    properties={
        'call_flag':relation(GentooCallFlagString),
    }
)
