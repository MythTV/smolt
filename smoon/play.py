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

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, eagerload
from playmodel import *


# ================================================================
# _SCALAR_DIFF_TEMPLATE
# ================================================================
_SCALAR_DIFF_TEMPLATE = """
try:
    %(current_name)s = %(tree_location)s
except KeyError:
    %(current_name)s = None

try:
    %(old_name)s = session.query(%(rel_class_name)s).options(eagerload('%(relation_name)s')).filter_by(machine_id=machine_id).one()
    old_value = %(old_name)s.%(relation_name)s.name
except sqlalchemy.orm.exc.NoResultFound:
    %(old_name)s = None
    old_value = None

# Calculate diff
if %(current_name)s != old_value:
    # Resolve diff
    if %(old_name)s:
        session.delete(%(old_name)s)
    if %(current_name)s:
        try:
            pool_object = session.query(%(pool_class_name)s).filter_by(name=%(current_name)s).one()
        except sqlalchemy.orm.exc.NoResultFound:
            pool_object = %(pool_class_name)s(%(current_name)s)
            session.add(pool_object)
            session.flush()
        session.add(%(rel_class_name)s(machine_id, pool_object.id))
session.flush()
"""


# ================================================================
# _VECTOR_DIFF_TEMPLATE
# ================================================================
_VECTOR_DIFF_TEMPLATE = """
try:
    %(current_name)s = %(tree_location)s
except KeyError:
    %(current_name)s = []
%(old_name)s = session.query(%(rel_class_name)s).options(eagerload('%(relation_name)s')).filter_by(machine_id=machine_id).all()

# Calculate diff
old_set = set(e.%(relation_name)s.name for e in %(old_name)s)
current_set = set(%(current_name)s)
strings_to_add = current_set - old_set
strings_to_remove = old_set - current_set

# Resolve diff
for i in strings_to_add:
    try:
        pool_object = session.query(%(pool_class_name)s).filter_by(name=i).one()
    except sqlalchemy.orm.exc.NoResultFound:
        pool_object = %(pool_class_name)s(i)
        session.add(pool_object)
        session.flush()
    session.add(%(rel_class_name)s(machine_id, pool_object.id))
for pool_object in %(old_name)s:
    name = pool_object.%(relation_name)s.name
    if name in strings_to_remove:
        session.delete(pool_object)
session.flush()
"""


# ================================================================
# _LOOKUP_OR_ADD_TEMPLATE
# ================================================================
_LOOKUP_OR_ADD_TEMPLATE = """
try:
    %(new_object_name)s = session.query(%(class_name)s).filter_by(name=%(source_var_name)s).one()
except sqlalchemy.orm.exc.NoResultFound:
    %(new_object_name)s = %(class_name)s(%(source_var_name)s)
    session.add(%(new_object_name)s)
"""


_DIFF_JOBS = [
    {'thing':'arch', 'foreign':'keyword', 'vector_flag':False, 'tree_location':"data['arch']"},
    {'thing':'chost', 'foreign':'chost', 'vector_flag':False, 'tree_location':"data['chost']"},
    {'thing':'distfiles_mirror', 'foreign':'mirror', 'vector_flag':True, 'tree_location':"data['mirrors']['distfiles']"},
    {'thing':'feature', 'foreign':'feature', 'vector_flag':True, 'tree_location':"data['features']"},
    {'thing':'global_use_flag', 'foreign':'use_flag', 'vector_flag':True, 'tree_location':"data['global_use_flags']"},
    {'thing':'overlay', 'foreign':'repository', 'vector_flag':True, 'tree_location':"data['overlays']"},
    {'thing':'sync_mirror', 'foreign':'mirror', 'vector_flag':False, 'tree_location':"data['mirrors']['sync']"},
    {'thing':'system_profile', 'foreign':'system_profile', 'vector_flag':False, 'tree_location':"data['system_profile']"},
]


def _current_var_name(middle, vector_flag):
    return 'current_%s_string%s' % (middle.rstrip('s'), numerus(vector_flag))

def _old_var_name(middle, vector_flag):
    return 'old_%s_object%s' % (middle.rstrip('s'), numerus(vector_flag))


def handle_gentoo_data(session, host_dict, machine_id):
    try:
        data = host_dict['distro_specific']['gentoo']
    except KeyError:
        logging.debug('No Gentoo-specific data')
        data = {}

    _handle_simple_stuff(session, data, machine_id)
    _handle_compile_flags(session, data, machine_id)
    _handle_accept_keywords(session, data, machine_id)
    _handle_package_mask(session, data, machine_id)
    _handle_installed_packages(session, data, machine_id)


def _handle_simple_stuff(session, data, machine_id):
    for job in _DIFF_JOBS:
        foreign = job['foreign']
        thing = job['thing']
        tree_location = job['tree_location']
        vector_flag = job['vector_flag']
        details = {
            'pool_class_name':pool_class_name(foreign, vector_flag=False),
            'rel_class_name':rel_class_name(thing),
            'relation_name':foreign,
            'tree_location':tree_location,
            'current_name':_current_var_name(thing, vector_flag),
            'old_name':_old_var_name(thing, vector_flag),
        }

        if vector_flag:
            program = _VECTOR_DIFF_TEMPLATE % details
        else:
            program = _SCALAR_DIFF_TEMPLATE % details
        dump_gentoo_python_code(program)
        exec(program)

def _handle_accept_keywords(session, data, machine_id):
    # Find current entries
    try:
        accept_keywords = data['accept_keywords']
    except KeyError:
        accept_keywords = {}
    current_accept_keywords_set = set()
    for i in accept_keywords:
        if i.startswith('~'):
            key = (i.lstrip('~'), False)
        else:
            key = (i, True)
        current_accept_keywords_set.add(key)

    # Find old entries
    old_accept_keywords_objects = session.query(\
            GentooAcceptKeywordRel).options(\
                eagerload('keyword')).\
            filter_by(machine_id=machine_id).all()
    old_accept_keywords_dict = {}
    for i in old_accept_keywords_objects:
        key = (i.keyword, bool(i.stable))
        old_accept_keywords_dict[key] = i
    old_accept_keywords_set = set(old_accept_keywords_dict.keys())

    # Calculate diff
    mappings_to_add = current_accept_keywords_set - old_accept_keywords_set
    mappings_to_remove = old_accept_keywords_set - current_accept_keywords_set

    # Resolve diff
    for i in mappings_to_remove:
        session.delete(old_accept_keywords_dict[i])
    for i in mappings_to_add:
        keyword, stable = i
        try:
            pool_object = session.query(GentooKeywordString).filter_by(name=keyword).one()
        except sqlalchemy.orm.exc.NoResultFound:
            pool_object = GentooKeywordString(keyword)
            session.add(pool_object)
            session.flush()
        keyword_id = pool_object.id
        session.add(GentooAcceptKeywordRel(machine_id, keyword_id, stable))
    session.flush()


def _handle_compile_flags(session, data, machine_id):
    for call_flag_class in ('CFLAGS', 'CXXFLAGS', 'LDFLAGS', 'MAKEOPTS'):
        try:
            call_flag_class_object = session.query(GentooCallFlagClassString).filter_by(name=call_flag_class).one()
        except sqlalchemy.orm.exc.NoResultFound:
            call_flag_class_object = GentooCallFlagClassString(call_flag_class)
            session.add(call_flag_class_object)
            session.flush()
        call_flag_class_id = call_flag_class_object.id

        # Find current entries
        try:
            current_call_flag_list = data['compile_flags'][call_flag_class]
        except KeyError:
            current_call_flag_list = []

        # Find old entries
        old_call_flag_objects = session.query(GentooCallFlagRel).options(\
                eagerload('call_flag')).\
            filter_by(machine_id=machine_id, call_flag_class_id=call_flag_class_id).all()

        # Re-construct call flag list
        old_call_flag_list = [a.call_flag.name for a in sorted(\
                [e for e in old_call_flag_objects], key=lambda x: x.position)]

        # Consistent data?
        if len(old_call_flag_list) != len(old_call_flag_objects):
            old_call_flag_list = None

        # Calculate diff
        if cmp(current_call_flag_list, old_call_flag_list) != 0:
            # Resolve diff
            for e in old_call_flag_objects:
                session.delete(e)
            for position, call_flag in enumerate(current_call_flag_list):
                try:
                    call_flag_object = session.query(GentooCallFlagString).filter_by(name=call_flag).one()
                except sqlalchemy.orm.exc.NoResultFound:
                    call_flag_object = GentooCallFlagString(call_flag)
                    session.add(call_flag_object)
                    session.flush()
                call_flag_id = call_flag_object.id
                session.add(GentooCallFlagRel(machine_id, call_flag_class_id, call_flag_id, position))
            session.flush()


def _handle_package_mask(session, data, machine_id):
    # Find current entries
    try:
        package_mask = data['user_package_mask']
    except KeyError:
        package_mask = {}
    current_package_mask_set = set()
    for package, atoms in package_mask.items():
        for i in atoms:
            key = (package, i)
            current_package_mask_set.add(key)

    # Find old entries
    old_package_mask_rel_objects = session.query(\
            GentooPackageMaskRel).options(\
                eagerload('package'), \
                eagerload('atom')).\
            filter_by(machine_id=machine_id).all()
    old_package_mask_dict = {}
    for e in old_package_mask_rel_objects:
        key = (e.package.name, e.atom.name)
        old_package_mask_dict[key] = e
    old_package_mask_set = set(old_package_mask_dict.keys())

    # Calculate diff
    mask_entries_to_add = current_package_mask_set - old_package_mask_set
    mask_entries_to_remove = old_package_mask_set - current_package_mask_set

    # Resolve diff
    for i in mask_entries_to_remove:
        session.delete(old_package_mask_dict[i])
    for i in mask_entries_to_add:
        package, atom = i
        lookup_or_add_jobs = (
            {'thing':'atom', },
            {'thing':'package', },
        )

        for job in lookup_or_add_jobs:
            thing = job['thing']
            details = {
                'class_name':pool_class_name(thing, vector_flag=False),
                'source_var_name':thing,
                'new_object_name':'%s_pool_object' % thing
            }

            program = _LOOKUP_OR_ADD_TEMPLATE % details
            dump_gentoo_python_code(program)
            exec(program)

        session.flush()
        package_id = package_pool_object.id
        atom_id = atom_pool_object.id

        mask_rel_object = GentooPackageMaskRel(machine_id, package_id, atom_id)
        session.add(mask_rel_object)


def _handle_installed_packages(session, data, machine_id):
    # Find old entries
    old_installed_package_rel_objects = session.query(\
            GentooInstalledPackagesRel).options(\
                eagerload('use_flags'), \
                eagerload('properties'), \
                eagerload('slot'), \
                eagerload('package')).\
            filter_by(machine_id=machine_id).all()
    old_install_set = set()
    for e in old_installed_package_rel_objects:
        key = (e.package.name, e.slot.name)
        old_install_set.add(key)

    # Find current entries
    try:
        installed_packages = data['installed_packages']
    except KeyError:
        installed_packages = []
    current_install_dict = {}
    for e in installed_packages:
        package, version, slot, keyword_status, masked, unmasked, \
                world, repository, use_flags = e
        key = (package, slot)
        current_install_dict[key] = e
    current_install_key_set = set(current_install_dict.keys())

    # Calculate diff
    installs_to_add = current_install_key_set - old_install_set
    installs_to_remove = old_install_set - current_install_key_set

    # Resolve diff
    for e in old_installed_package_rel_objects:
        key = (e.package.name, e.slot.name)
        if key in installs_to_remove:
            session.delete(e)
    for key in installs_to_add:
        package, version, slot, keyword_status, \
                masked, unmasked, world, repository, \
                use_flags = current_install_dict[key]

        lookup_or_add_jobs = (
            {'thing':'slot', },
            {'thing':'package', },
            {'thing':'version', },
            {'thing':'repository', },
        )

        for job in lookup_or_add_jobs:
            thing = job['thing']
            details = {
                'class_name':pool_class_name(thing, vector_flag=False),
                'source_var_name':thing,
                'new_object_name':'%s_pool_object' % thing
            }

            program = _LOOKUP_OR_ADD_TEMPLATE % details
            dump_gentoo_python_code(program)
            exec(program)

        session.flush()
        package_id = package_pool_object.id
        slot_id = slot_pool_object.id

        # Add install
        install_object = GentooInstalledPackagesRel(machine_id, package_id, slot_id)
        session.add(install_object)

        # Lookup/add use flags
        use_flag_pool_objects = session.query(GentooUseFlagString).filter(GentooUseFlagString.name.in_(use_flags)).all()
        use_flag_dict = {}
        for i in use_flag_pool_objects:
            use_flag_dict[i.name] = i
        for i in [e for e in use_flags if not e in use_flag_dict]:
            use_flag_object = GentooUseFlagString(i)
            use_flag_dict[i] = use_flag_object
            session.add(use_flag_object)

        session.flush()
        install_id = install_object.id
        version_id = version_pool_object.id
        repository_id = repository_pool_object.id

        # Relate use flags
        install_object.use_flags = []
        for v in use_flag_dict.values():
            use_flag_id = v.id
            use_flag_rel_object = GentooInstalledPackageUseFlagRel(install_id, use_flag_id)
            install_object.use_flags.append(use_flag_rel_object)

        # Add properties
        install_object.properties = [GentooInstalledPackagePropertiesRel(\
                install_id, version_id, keyword_status_code(keyword_status),
                masked, unmasked, world, repository_id), ]

    session.flush()


if __name__ == '__main__':
    CONNECTION = 'mysql://smoon:smoon@localhost/smoon'
    #ECHO=True
    ECHO=False
    DROP=True
    #DROP=False
    machine_id = 3

    print sqlalchemy.__version__

    engine = create_engine(CONNECTION, echo=ECHO)
    session = sessionmaker(bind=engine)()

    if DROP:
        metadata.drop_all(engine)
    metadata.create_all(engine, checkfirst=(not DROP))

    import sys
    import os
    sys.path.append(os.path.join(sys.path[0], '..', 'client', 'distros'))
    sys.path.append(os.path.join(sys.path[0], '..', 'client'))
    from distros.gentoo.main import Gentoo

    gentoo = Gentoo()
    gentoo.gather()

    host_dict = {
        'distro_specific':{
            'gentoo':gentoo.data()
        }
    }

    handle_gentoo_data(session, host_dict, machine_id)
