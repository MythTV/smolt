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


class ClassNameCollision(Exception):
    pass


def _register_class(class_name, class_object):
    if class_name in globals():
        raise ClassNameCollision
    class_object.__name__ = class_name
    globals()[class_name] = class_object


_pool_tables = {
    'keyword':{'pool_type':CHAR(127)},
    'chost':{'pool_type':CHAR(255)},
    'compile_flag':{'pool_type':CHAR(255)},
    'mirror':{'pool_type':CHAR(255)},
    'overlay':{'pool_type':CHAR(127)},
    'feature':{'pool_type':CHAR(127)},
    'package':{'pool_type':CHAR(127)},
#   'use_flag':{'pool_type':CHAR(127)},
}

_map_tables = {
    'archs':{'foreign_name':'keyword', 'vector':False},
    'chosts':{'foreign_name':'chost', 'vector':False},
    'sync_mirrors':{'foreign_name':'mirror', 'vector':False},
    'keywords':{'foreign_name':'keyword', 'vector':True},
    'cflags':{'foreign_name':'compile_flag', 'vector':True},
    'cxxflags':{'foreign_name':'compile_flag', 'vector':True},
    'ldflags':{'foreign_name':'compile_flag', 'vector':True},
    'makeopts':{'foreign_name':'compile_flag', 'vector':True},
    'features':{'foreign_name':'feature', 'vector':True},
    'distfiles_mirrors':{'foreign_name':'mirror', 'vector':True},
#   'global_use_flags':{'foreign_name':'use_flag', 'vector':True},
}

_generated_tables = {}

for k, v in _pool_tables.items():
    table_name = 'gentoo_%s_pool' % k
    class_name = 'Gentoo%sString' % k.title().replace('_', '')
    pool_type = v['pool_type']
    logging.debug('Generating table "%s" and related class "%s"...' % (table_name, class_name))

    # Create table
    _generated_tables[table_name] = Table(table_name, metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('name', pool_type, unique=True),
    )

    # Create class
    class generated_class_object(object):
        def __init__(self, name):
            self.name = name
    _register_class(class_name, generated_class_object)

    # Setup mapping
    mapper(generated_class_object, _generated_tables[table_name])

    # Store names for use by other tables
    v['table_name'] = table_name
    v['class_name'] = class_name


for k, v in _map_tables.items():
    table_name = 'gentoo_%s' % k
    class_name = 'Gentoo%s' % k.rstrip('s').title().replace('_', '')
    foreign_column_name = '%s_id' % v['foreign_name']
    foreign_relation_name = v['foreign_name']
    foreign_key_name = '%s.id' % _pool_tables[v['foreign_name']]['table_name']
    foreign_key_class_name = _pool_tables[v['foreign_name']]['class_name']
    foreign_key_class = globals()[foreign_key_class_name]
    vector = v['vector']
    logging.info('Generating table "%s" and related class "%s"...' % (table_name, class_name))

    # Create table
    if vector:
        _generated_tables[table_name] = Table(table_name, metadata,
            Column('id', Integer, primary_key=True, autoincrement=True),
            Column('machine_id', Integer),
            Column(foreign_column_name, Integer, ForeignKey(foreign_key_name)),
            UniqueConstraint('machine_id', foreign_column_name),
        )
    else:
        _generated_tables[table_name] = Table(table_name, metadata,
            Column('id', Integer, primary_key=True, autoincrement=True),
            Column('machine_id', Integer, unique=True),
            Column(foreign_column_name, Integer, ForeignKey(foreign_key_name)),
        )

    # Create class
    class generated_class_object(object):
        def __init__(self, machine_id, foreign_id):
            self.machine_id = machine_id
            setattr(self, foreign_column_name, foreign_id)
    _register_class(class_name, generated_class_object)

    # Setup mapping
    mapper(generated_class_object, _generated_tables[table_name],
        properties={
            foreign_relation_name:relation(foreign_key_class),
        }
    )

# TODO
#     packages
#     package use flags


# =========================================================
# gentoo_use_flag_pool
# =========================================================
_gentoo_use_flag_pool_table = Table('gentoo_use_flag_pool', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', CHAR(255), unique=True),
)

class GentooUseFlagString(object):
    def __init__(self, name):
        self.name = name

mapper(GentooUseFlagString, _gentoo_use_flag_pool_table)


# =========================================================
# gentoo_global_use_flags
# =========================================================
_gentoo_global_use_flags_table = Table('gentoo_global_use_flags', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('machine_id', Integer),
    Column('use_flag_id', Integer, ForeignKey('gentoo_use_flag_pool.id')),
    UniqueConstraint('machine_id', 'use_flag_id'),
)

class GentooGlobalUseFlag(object):
    def __init__(self, machine_id, use_flag_id):
        self.machine_id = machine_id
        self.use_flag_id = use_flag_id

mapper(GentooGlobalUseFlag, _gentoo_global_use_flags_table,
    properties={
        'use_flag':relation(GentooUseFlagString),
    }
)
