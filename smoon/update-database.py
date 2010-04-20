#! /usr/bin/python

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

from hardware.model import *
from hardware.hwdata import DeviceMap

# first look on the command line for a desired config file,
# if it's not on the command line, then
# look for setup.py in this directory. If it's not there, this script is
# probably installed
if len(sys.argv) > 1:
    update_config(configfile=sys.argv[1],
        modulename="hardware.config")
elif path.exists(path.join(path.dirname(__file__), "setup.py")):
    update_config(configfile="dev.cfg",modulename="hardware.config")
else:
    update_config(configfile="prod.cfg",modulename="hardware.config")

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


