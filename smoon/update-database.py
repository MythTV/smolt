#!/usr/bin/python
# -*- coding: utf-8 -*-
# smolt - Fedora hardware profiler
#
# Copyright (C) 2007 Mike McGrath
# Copyright (C) 2010 Sebastian Pipping <sebastian@pipping.org>
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

from __future__ import with_statement

database_ddl_dir = "../database/"

__requires__ = "Turbogears[future]"
import pkg_resources
pkg_resources.require("TurboGears")

from turbogears import view, database, errorhandling, config
from turbogears import update_config, start_server
import sys
import time
import os
import re
from turbogears.database import get_engine, metadata, mapper

import os.path as path
import itertools as iter

from sqlalchemy import *
import sqlalchemy.sql as sql


from hardware.featureset import init, config_filename
_cfg_filename = None
if len(sys.argv) > 1:
    _cfg_filename = sys.argv[1]

init(_cfg_filename)
update_config(configfile=config_filename(),modulename="hardware.config")


from hardware.model import *
from hardware.hwdata import DeviceMap


from turbogears.database import session
past_changes = session.query(SchemaChange).all()

def flatten(listOfLists):
    return list(iter.chain(*listOfLists))

def files_for_dir(dir, files):
    return ((path.join(dir, file), file) for file in files)

db_files = (files_for_dir(dir, files)
            for dir, ignore, files in os.walk(database_ddl_dir))

db_files = iter.chain(*db_files)

upd_pat = re.compile(r'db([0-9]*)\.([0-9]*)\.([0-9]*)\.(\w*)\.(.*)sql$')

update_files = ((full_name, upd_pat.match(name))
                for full_name, name
                in db_files
                if (upd_pat.match(name)))

update_files = ((name, match.groups()) for name, match in update_files)

col_names = ['major', 'minor', 'point', 'branch', 'name']

update_files = ((name, dict(zip(col_names, gs)))
                for name, gs in update_files)

def convert(data, name, fun):
    data[name] = fun(data[name])
    return data

update_files = ((file, convert(data, 'major', int)) for file, data in update_files)
update_files = ((file, convert(data, 'minor', int)) for file, data in update_files)
update_files = ((file, convert(data, 'point', int)) for file, data in update_files)

def cmp_for_schema_change(a, b):
    print a, b
    #there has to be a better way!
    if a['major'] < b['major']:
        return -1
    elif a['major'] > b['major']:
        return 1
    else:
        if a['minor'] < b['minor']: #or c-sharp
            return -1
        elif a['minor'] > b['minor']:
            return 1
        else:
            return cmp(a['point'], b['point'])

update_files = sorted(update_files, lambda a,b: cmp_for_schema_change(a[1], b[1]))

def apply_change(file):
    text = open(file).read()
    print "applying ", file
    s = sql.text(text)
    get_engine().execute(s)

for file, data in update_files:
    with session.begin_nested():
        if not session.query(SchemaChange).filter_by(**data).all():
            apply_change(file)
            new_change = SchemaChange(**data)
            session.save(new_change)


