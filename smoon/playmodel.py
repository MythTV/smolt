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
from sqlalchemy import Table, Column, Integer, CHAR, ForeignKey, UniqueConstraint, MetaData
from sqlalchemy.orm import mapper, relation
metadata = MetaData()


_pool_table_jobs = [
    {'thing':'atom', 'col_type':'CHAR(255)'},
    {'thing':'cflag', 'col_type':'CHAR(255)'},
    {'thing':'chost', 'col_type':'CHAR(255)'},
    {'thing':'cxxflag', 'col_type':'CHAR(255)'},
    {'thing':'feature', 'col_type':'CHAR(127)'},
    {'thing':'ldflag', 'col_type':'CHAR(255)'},
    {'thing':'makeopt', 'col_type':'CHAR(255)'},
    {'thing':'keyword', 'col_type':'CHAR(127)'},
    {'thing':'mirror', 'col_type':'CHAR(255)'},
    {'thing':'package', 'col_type':'CHAR(255)'},
    {'thing':'repository', 'col_type':'CHAR(127)'},
    {'thing':'system_profile', 'col_type':'CHAR(255)'},
    {'thing':'use_flag', 'col_type':'CHAR(127)'},
    {'thing':'version', 'col_type':'CHAR(127)'},
]

_rel_table_jobs = [
    {'thing':'accept_keywords', 'foreign':'keyword', 'vector':True},
    {'thing':'archs', 'foreign':'keyword', 'vector':False},
    {'thing':'chosts', 'foreign':'chost', 'vector':False},
    {'thing':'sync_mirrors', 'foreign':'mirror', 'vector':False},
    {'thing':'cflags', 'foreign':'cflag', 'vector':True},
    {'thing':'cxxflags', 'foreign':'cxxflag', 'vector':True},
    {'thing':'distfiles_mirrors', 'foreign':'mirror', 'vector':True},
    {'thing':'features', 'foreign':'feature', 'vector':True},
    {'thing':'global_use_flags', 'foreign':'use_flag', 'vector':True},
    {'thing':'ldflags', 'foreign':'ldflag', 'vector':True},
    {'thing':'makeopts', 'foreign':'makeopt', 'vector':True},
    {'thing':'overlays', 'foreign':'repository', 'vector':True},
    {'thing':'system_profile', 'foreign':'system_profile', 'vector':False},
]


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


def _pool_table_name(middle):
    return 'gentoo_%s_pool' % middle.rstrip('s')

def _pool_table_instance(middle):
    return '_gentoo_%s_pool_table' % middle.rstrip('s')

def _pool_class_name(middle):
    return 'Gentoo%sString' % middle.title().replace('_', '')

def _rel_table_name(middle):
    return 'gentoo_%s_rel' % middle.rstrip('s')

def _rel_table_instance(middle):
    return '_gentoo_%s_rel_table' % middle.rstrip('s')

def _rel_class_name(middle):
    return 'Gentoo%s' % middle.rstrip('s').title().replace('_', '')

def _foreign_key_column(middle):
    return '%s_id' % middle.rstrip('s')


# Create pool tables
for job in _pool_table_jobs:
    thing = job['thing']
    col_type = job['col_type']
    details = {
        'table_name':_pool_table_name(thing),
        'table_var_name':_pool_table_instance(thing),
        'class_name':_pool_class_name(thing),
        'col_type':col_type,
    }
    logging.debug('Generating table "%(table_name)s" and related class "%(class_name)s"...' % details)
    program = _POOL_TABLE_TEMPLATE % details
    print "========================="
    print program
    print "========================="
    exec(program)


# Create relation tables
for job in _rel_table_jobs:
    thing = job['thing']
    foreign = job['foreign']
    vector = job['vector']
    details = {
        'table_name':_rel_table_name(thing),
        'table_var_name':_rel_table_instance(thing),
        'class_name':_rel_class_name(thing),
        'foreign_key_table':_pool_table_name(foreign),
        'foreign_key_column':_foreign_key_column(foreign),
        'foreign_key_class':_pool_class_name(foreign),
        'relation_name':foreign,
    }
    logging.debug('Generating table "%(table_name)s" and related class "%(class_name)s"...' % details)
    if vector:
        program = _VECTOR_REL_TABLE_TEMPLATE % details
    else:
        program = _SCALAR_REL_TABLE_TEMPLATE % details
    print "========================="
    print program
    print "========================="
    exec(program)
