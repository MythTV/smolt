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

# =========================================================
# Config
# =========================================================
CONNECTION = 'mysql://smoon:smoon@localhost/smoon'
ECHO=True
#ECHO=False
#DROP=True
DROP=False
machine_id = 3

# =========================================================
# Imports
# =========================================================
import sqlalchemy
print sqlalchemy.__version__
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, eagerload
from playmodel import *

# =========================================================
# Setup
# =========================================================
engine = create_engine(CONNECTION, echo=ECHO)
session = sessionmaker(bind=engine)()

if DROP:
    metadata.drop_all(engine)
metadata.create_all(engine)

# Gather old and new data
import sys
import os
sys.path.append(os.path.join(sys.path[0], '..', 'client', 'distros'))
sys.path.append(os.path.join(sys.path[0], '..', 'client'))
from distros.gentoo.main import Gentoo

gentoo = Gentoo()
gentoo.gather()
data = gentoo.data()


_SCALAR_DIFF_TEMPLATE = """
try:
    %(current_name)s = %(tree_location)s
except KeyError:
    raise # TODO
%(old_name)s = None
try:
    %(old_name)s = session.query(%(rel_class_name)s).options(eagerload('%(relation_name)s')).filter_by(machine_id=machine_id).one()
    old_value = %(old_name)s.%(relation_name)s.name
except sqlalchemy.orm.exc.NoResultFound:
    old_value = None

# Calculate diff
current_value = %(current_name)s
if current_value != old_value:
    # Apply diff
    if %(old_name)s:
        print 'DEL', old_value
        session.delete(%(old_name)s)
    try:
        pool_object = session.query(%(pool_class_name)s).filter_by(name=current_value).one()
    except sqlalchemy.orm.exc.NoResultFound:
        pool_object = %(pool_class_name)s(current_value)
        session.add(pool_object)
        session.flush()
    print 'ADD', pool_object.name
    session.add(%(rel_class_name)s(machine_id, pool_object.id))
session.flush()
"""


_VECTOR_DIFF_TEMPLATE = """
try:
    %(current_name)s = %(tree_location)s
except KeyError:
    raise # TODO
%(old_name)s = session.query(%(rel_class_name)s).options(eagerload('%(relation_name)s')).filter_by(machine_id=machine_id).all()

# Calculate diff
old_set = set(e.%(relation_name)s.name for e in %(old_name)s)  # EAGERLOAD for this line
current_set = set(%(current_name)s)
strings_to_add = current_set - old_set
strings_to_remove = old_set - current_set

# Apply diff
for i in strings_to_add:
    try:
        pool_object = session.query(%(pool_class_name)s).filter_by(name=i).one()
    except sqlalchemy.orm.exc.NoResultFound:
        pool_object = %(pool_class_name)s(i)
        session.add(pool_object)
        session.flush()
    print 'ADD', pool_object.name
    session.add(%(rel_class_name)s(machine_id, pool_object.id))
for pool_object in %(old_name)s:
    name = pool_object.%(relation_name)s.name
    if name in strings_to_remove:
        print 'DEL', name
        session.delete(pool_object)
session.flush()
"""


def _current_var_name(middle, vector):
    return 'current_%s_string%s' % (middle.rstrip('s'), vector and 's' or '')

def _old_var_name(middle, vector):
    return 'old_%s_object%s' % (middle.rstrip('s'), vector and 's' or '')


diff_jobs = [
    {'thing':'arch', 'foreign':'keyword', 'vector':False, 'tree_location':"data['arch']"},
    {'thing':'accept_keywords', 'foreign':'keyword', 'vector':True, 'tree_location':"data['accept_keywords']"},
    {'thing':'cflags', 'foreign':'cflag', 'vector':True, 'tree_location':"data['compile_flags']['CFLAGS']"},
    {'thing':'chost', 'foreign':'chost', 'vector':False, 'tree_location':"data['chost']"},
    {'thing':'cxxflags', 'foreign':'cxxflag', 'vector':True, 'tree_location':"data['compile_flags']['CXXFLAGS']"},
    {'thing':'distfiles_mirrors', 'foreign':'mirror', 'vector':True, 'tree_location':"data['mirrors']['distfiles']"},
    {'thing':'features', 'foreign':'feature', 'vector':True, 'tree_location':"data['features']"},
    {'thing':'global_use_flags', 'foreign':'use_flag', 'vector':True, 'tree_location':"data['global_use_flags']"},
    {'thing':'ldflags', 'foreign':'ldflag', 'vector':True, 'tree_location':"data['compile_flags']['LDFLAGS']"},
    {'thing':'makeopts', 'foreign':'makeopt', 'vector':True, 'tree_location':"data['compile_flags']['MAKEOPTS']"},
    {'thing':'overlays', 'foreign':'repository', 'vector':True, 'tree_location':"data['overlays']"},
    {'thing':'sync_mirror', 'foreign':'mirror', 'vector':False, 'tree_location':"data['mirrors']['sync']"},
    {'thing':'system_profile', 'foreign':'system_profile', 'vector':False, 'tree_location':"data['system_profile']"},
]


for job in diff_jobs:
    foreign = job['foreign']
    thing = job['thing']
    tree_location = job['tree_location']
    vector = job['vector']
    details = {
        'pool_class_name':pool_class_name(foreign),
        'rel_class_name':rel_class_name(thing),
        'relation_name':foreign,
        'tree_location':tree_location,
        'current_name':_current_var_name(thing, vector),
        'old_name':_old_var_name(thing, vector),
    }

    if vector:
        program = _VECTOR_DIFF_TEMPLATE % details
    else:
        program = _SCALAR_DIFF_TEMPLATE % details
    print "========================="
    print program
    print "========================="
    exec(program)
