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

from playmodel import *
from playmodel import _gentoo_distfiles_mirrors_table, _gentoo_mirror_pool_table
from playmodel import _gentoo_accept_keywords_table, _gentoo_keyword_pool_table
from playmodel import _gentoo_features_table, _gentoo_feature_pool_table
from playmodel import _gentoo_global_use_flags_table, _gentoo_use_flag_pool_table
from playmodel import _gentoo_sync_mirror_table, _gentoo_mirror_pool_table
from playmodel import _gentoo_system_profile_table, _gentoo_system_profile_pool_table
from playmodel import _gentoo_chost_table, _gentoo_chost_pool_table
from playmodel import _gentoo_call_flags_table, _gentoo_call_flag_pool_table
from playmodel import _gentoo_package_mask_table, _gentoo_package_pool_table, _gentoo_atom_pool_table
from playmodel import _gentoo_repo_pool_table, _gentoo_repos_table
from playmodel import _gentoo_installed_packages_table, _gentoo_installed_package_props_table
from playmodel import _gentoo_version_pool_table, _gentoo_slot_pool_table
import datetime
import sqlalchemy
from sqlalchemy.sql import func, select, join, and_, text

import sys
if 'turbogears' in sys.modules:
    logging.debug('Turbogears context')
    from turbogears.database import metadata
else:
    logging.debug('Plain SQL alchemy context')
    from sqlalchemy import MetaData
    metadata = MetaData()


_MAX_DISTFILES_MIRRORS = 30
_MAX_FEATURES = 30
_MAX_GLOBAL_USE_FLAGS = 100
_MAX_SYNC_MIRRORS = 30
_MAX_SYSTEM_PROFILE = 30
_MAX_CHOST = 30
_MAX_CALL_FLAGS = 30
_MAX_PACKAGE_MASK_ENTRIES = 30
_MAX_PACKAGE_MASK_SUB_ENTRIES = 5
_MAX_INSTALLED_PACKAGES = 100
_MAX_INSTALLED_PACKAGE_SLOTS = 1
_MAX_INSTALLED_PACKAGE_SLOT_VERSIONS = 1


class GentooReporter:
    def __init__(self, session):
        self.session = session
        self.gentoo_machines = 1
        self._data = {}

    def _relative(self, absolute, hundred, post_dot_digits=1):
        format = '%%.0%df' % post_dot_digits
        return format % round(int(absolute) * 100.0 / hundred, post_dot_digits)

    def _analyze_archs(self):
        # TODO use different type of join?
        def make_row(absolute_stable, absolute_unstable, absolute_total, label=None):
            res = {
                'absolute_stable':absolute_stable,
                'absolute_unstable':absolute_unstable,
                'absolute_total':absolute_total,
                'relative_stable':self._relative(absolute_stable, self.gentoo_machines),
                'relative_unstable':self._relative(absolute_unstable, self.gentoo_machines),
                'relative_total':self._relative(absolute_total, self.gentoo_machines),
            }
            if label != None:
                res['label'] = label
            return res

        columns = [GentooKeywordString.name, func.count(GentooAcceptKeywordRel.machine_id), func.sum(GentooAcceptKeywordRel.stable)]
        pool_join = _gentoo_accept_keywords_table.join(_gentoo_keyword_pool_table)
        query = select(columns, from_obj=[pool_join]).\
                group_by(GentooAcceptKeywordRel.keyword_id).order_by(\
                func.count(GentooAcceptKeywordRel.machine_id).desc())
        total_stable = 0
        total_unstable = 0
        total_total = 0
        final_rows = []
        for i in query.execute().fetchall():
            label, total, stable = i
            stable = long(stable)
            unstable = total - stable
            if unstable < 0:
                unstable = 0

            total_stable = total_stable + stable
            total_unstable = total_unstable + unstable
            total_total = total_total + total

            final_rows.append(make_row(stable, unstable, total, label))

        res = {
            'listed':final_rows,
            'total':[make_row(total_stable, total_unstable, total_total)],
        }
        return res

    def _analyzes_repos(self):
        package_count = select([func.count(GentooInstalledPackagesRel.package_id.distinct())]).execute().fetchall()[0][0]
        installation_count = select([func.count(GentooInstalledPackagesRel.id)]).execute().fetchall()[0][0]

        def make_row(absolute_popularity, absolute_used_packages, absolute_total_installations, label=None):
            res = {
                'absolute_popularity':absolute_popularity,
                'absolute_used_packages':absolute_used_packages,
                'absolute_total_installations':absolute_total_installations,
                'relative_popularity':self._relative(absolute_popularity, self.gentoo_machines),
                'relative_used_packages':self._relative(absolute_used_packages, package_count),
                'relative_total_installations':self._relative(absolute_total_installations, installation_count),
            }
            if label != None:
                res['label'] = label
            return res

        columns = [GentooRepoString.name, GentooRepoRel.repo_id, func.count(GentooRepoRel.machine_id)]
        pool_join = _gentoo_repos_table.join(_gentoo_repo_pool_table)
        query = select(columns, from_obj=[pool_join]).\
                group_by(GentooRepoRel.repo_id).order_by(\
                func.count(GentooRepoRel.machine_id).desc())

        repo_stats = {}
        for i in query.execute().fetchall():
            name, repo_id, machine_count = i
            repo_stats[repo_id] = { 'name':name,
                                    'machine_count':machine_count,
                                    'used_packages':0,
                                    'total_installations':0}

        install_join = _gentoo_installed_packages_table.join(
                _gentoo_installed_package_props_table).join(_gentoo_repo_pool_table)
        install_columns = [ GentooInstalledPackagePropertiesRel.repo_id, \
                            GentooRepoString.name, \
                            func.count(GentooInstalledPackagesRel.package_id.distinct()), \
                            func.count(GentooInstalledPackagesRel.id.distinct())]
        install_query = select(install_columns, from_obj=[install_join, ]).\
                group_by(GentooInstalledPackagePropertiesRel.repo_id)
        for i in install_query.execute().fetchall():
            repo_id, repo_name, used_packages, total_installations = i
            if repo_id in repo_stats:
                repo_stats[repo_id]['used_packages'] = used_packages
                repo_stats[repo_id]['total_installations'] = total_installations
            else:
                repo_stats[repo_id] = { 'name':repo_name,
                                        'machine_count':0,
                                        'used_packages':used_packages,
                                        'total_installations':total_installations}

        total_total_installations = 0
        final_rows = []
        def repo_cmp(a, b):
            res = cmp(a['machine_count'], b['machine_count'])
            if res != 0:
                return -res
            res = cmp(a['name'], b['name'])
            if res != 0:
                return res
            return 0

        for _, v in sorted(repo_stats.items(), cmp=\
                lambda a, b: repo_cmp(a[1], b[1])):
            repo_name = v['name']
            popularity = v['machine_count']
            used_packages = v['used_packages']
            total_installations = v['total_installations']

            final_rows.append(make_row(popularity, used_packages, total_installations, repo_name))
            total_total_installations = total_total_installations + total_installations

        res = {
            'listed':final_rows,
            'total':[make_row(self.gentoo_machines, package_count, total_total_installations)],
        }
        return res

    def _analyze_simple_stuff(self):
        def make_row(absolute, post_dot_digits, label=None):
            res = {
                'absolute':absolute,
                'relative':self._relative(absolute, self.gentoo_machines, post_dot_digits),
            }
            if label != None:
                res['label'] = label
            return res

        jobs = [
            {'_SECTION':'distfiles_mirrors',
                '_POOL_TABLE_OBJECT':_gentoo_mirror_pool_table,
                '_REL_TABLE_OBJECT':_gentoo_distfiles_mirrors_table,
                '_REL_CLASS_OBJECT':GentooDistfilesMirrorRel,
                '_POOL_CLASS_OBJECT':GentooMirrorString,
                '_DISPLAY_LIMIT':_MAX_DISTFILES_MIRRORS,
                '_FOREIGN_COLUMN_NAME':'mirror_id'},
            {'_SECTION':'features',
                '_POOL_TABLE_OBJECT':_gentoo_feature_pool_table,
                '_REL_TABLE_OBJECT':_gentoo_features_table,
                '_REL_CLASS_OBJECT':GentooFeatureRel,
                '_POOL_CLASS_OBJECT':GentooFeatureString,
                '_DISPLAY_LIMIT':_MAX_FEATURES,
                '_FOREIGN_COLUMN_NAME':'feature_id'},
            {'_SECTION':'sync_mirror',
                '_POOL_TABLE_OBJECT':_gentoo_mirror_pool_table,
                '_REL_TABLE_OBJECT':_gentoo_sync_mirror_table,
                '_REL_CLASS_OBJECT':GentooSyncMirrorRel,
                '_POOL_CLASS_OBJECT':GentooMirrorString,
                '_DISPLAY_LIMIT':_MAX_SYNC_MIRRORS,
                '_FOREIGN_COLUMN_NAME':'mirror_id'},
            {'_SECTION':'system_profile',
                '_POOL_TABLE_OBJECT':_gentoo_system_profile_pool_table,
                '_REL_TABLE_OBJECT':_gentoo_system_profile_table,
                '_REL_CLASS_OBJECT':GentooSystemProfileRel,
                '_POOL_CLASS_OBJECT':GentooSystemProfileString,
                '_DISPLAY_LIMIT':_MAX_SYSTEM_PROFILE,
                '_FOREIGN_COLUMN_NAME':'system_profile_id'},
            {'_SECTION':'chost',
                '_POOL_TABLE_OBJECT':_gentoo_chost_pool_table,
                '_REL_TABLE_OBJECT':_gentoo_chost_table,
                '_REL_CLASS_OBJECT':GentooChostRel,
                '_POOL_CLASS_OBJECT':GentooChostString,
                '_DISPLAY_LIMIT':_MAX_CHOST,
                '_FOREIGN_COLUMN_NAME':'chost_id'},
        ]

        res = {}
        for j in jobs:
            _SECTION = j['_SECTION']
            _POOL_TABLE_OBJECT = j['_POOL_TABLE_OBJECT']
            _REL_TABLE_OBJECT = j['_REL_TABLE_OBJECT']
            _REL_CLASS_OBJECT = j['_REL_CLASS_OBJECT']
            _POOL_CLASS_OBJECT = j['_POOL_CLASS_OBJECT']
            _DISPLAY_LIMIT = j['_DISPLAY_LIMIT']
            _FOREIGN_COLUMN_NAME = j['_FOREIGN_COLUMN_NAME']

            pool_join = _REL_TABLE_OBJECT.join(_POOL_TABLE_OBJECT)
            total_entry_count = self.session.query(_REL_CLASS_OBJECT).count()
            query = select([_POOL_CLASS_OBJECT.name, func.count(_REL_CLASS_OBJECT.machine_id)], \
                    from_obj=[pool_join]).group_by(getattr(_REL_CLASS_OBJECT, _FOREIGN_COLUMN_NAME)).order_by(\
                    func.count(_REL_CLASS_OBJECT.machine_id).desc(), _POOL_CLASS_OBJECT.name).limit(_DISPLAY_LIMIT)
            if _DISPLAY_LIMIT >= 50:
                post_dot_digits = 2
            else:
                post_dot_digits = 1

            final_rows = []
            others = total_entry_count
            for i in query.execute().fetchall():
                label, absolute = i
                others = others - absolute
                final_rows.append(make_row(absolute, post_dot_digits, label))
            if others < 0:
                others = 0

            res[_SECTION] = {
                'listed':final_rows,
                'others':[make_row(others, post_dot_digits)],
                'total':[make_row(total_entry_count, post_dot_digits)],
            }
        return res

    def _analyze_global_use_flags(self):
        def make_row(absolute, post_dot_digits, label=None):
            res = {
                'absolute':absolute,
                'relative':self._relative(absolute, self.gentoo_machines, post_dot_digits),
            }
            if label != None:
                res['label'] = label
            return res

        pool_join = _gentoo_global_use_flags_table.join(_gentoo_use_flag_pool_table)
        total_entry_count = self.session.query(GentooGlobalUseFlagRel).\
                filter_by(set_in_make_conf=1).count()
        query = select([GentooUseFlagString.name, func.count(GentooGlobalUseFlagRel.machine_id)], \
                from_obj=[pool_join]).group_by(GentooGlobalUseFlagRel.use_flag_id).\
                where(and_(GentooGlobalUseFlagRel.set_in_make_conf == 1, \
                    GentooGlobalUseFlagRel.enabled_in_make_conf == 1)).order_by(\
                func.count(GentooGlobalUseFlagRel.machine_id).desc(), GentooUseFlagString.name).limit(_MAX_GLOBAL_USE_FLAGS)
        if _MAX_GLOBAL_USE_FLAGS >= 50:
            post_dot_digits = 2
        else:
            post_dot_digits = 1

        final_rows = []
        others = total_entry_count
        for i in query.execute().fetchall():
            label, absolute = i
            others = others - absolute
            final_rows.append(make_row(absolute, post_dot_digits, label))
        if others < 0:
            others = 0

        res = {
            'listed':final_rows,
            'others':[make_row(others, post_dot_digits)],
            'total':[make_row(total_entry_count, post_dot_digits)],
        }
        return res

    def _analyzes_package_mask(self):
        def make_row(absolute, post_dot_digits, label=None):
            res = {
                'absolute':absolute,
                'relative':self._relative(absolute, self.gentoo_machines, post_dot_digits),
            }
            if label != None:
                res['label'] = label
            return res

        post_dot_digits = 1

        machine_count_list =  select([func.count(GentooPackageMaskRel.machine_id.distinct())]).group_by(GentooPackageMaskRel.package_id).execute().fetchall()
        total_entry_count = sum(e[0] for e in machine_count_list)
        others = total_entry_count

        pool_join = _gentoo_package_mask_table.join(_gentoo_package_pool_table)
        query = select([
                    GentooPackageString.name,
                    GentooPackageMaskRel.package_id,
                    func.count(GentooPackageMaskRel.atom_id),
                    func.count(GentooPackageMaskRel.machine_id.distinct())],
                from_obj=[pool_join]).\
                group_by(
                    GentooPackageMaskRel.package_id).\
                order_by(
                    func.count(GentooPackageMaskRel.machine_id.distinct()).desc(),
                    GentooPackageString.name).\
                limit(_MAX_PACKAGE_MASK_ENTRIES)
        final_rows = []
        for package_entry in query.execute().fetchall():
            package_name, package_id, atom_count, machine_count = package_entry
            others = others - machine_count
            row = {}
            row['package'] = package_name
            details = []
            if atom_count > 1:
                pool_join = _gentoo_package_mask_table.join(_gentoo_atom_pool_table)
                query = select([
                            GentooAtomString.name,
                            func.count(GentooPackageMaskRel.machine_id)],
                        from_obj=[pool_join]).\
                        where(
                            GentooPackageMaskRel.package_id == package_id).\
                        group_by(GentooPackageMaskRel.atom_id).\
                        order_by(
                            func.count(GentooPackageMaskRel.machine_id).desc(),
                            GentooAtomString.name).\
                        limit(_MAX_PACKAGE_MASK_SUB_ENTRIES)
                for atom_entry in query.execute().fetchall():
                    atom, count = atom_entry
                    details.append(make_row(count, post_dot_digits, atom))
            else:
                pool_join = _gentoo_package_mask_table.join(_gentoo_atom_pool_table)
                query = select([
                            GentooAtomString.name],
                        from_obj=[pool_join]).\
                        where(
                            GentooPackageMaskRel.package_id == package_id).\
                        limit(1)
                atom_name = query.execute().fetchall()[0][0]
                details.append(make_row(atom_count, post_dot_digits, atom_name))
            row['any'] = make_row(machine_count, post_dot_digits)
            row['details'] = details
            final_rows.append(row)

        if others < 0:
            others = 0

        res = {
            'listed':final_rows,
            'others':[make_row(others, post_dot_digits)],
            'total':[make_row(total_entry_count, post_dot_digits)],
        }
        return res

    def _analyzes_installed_packages_most_installed_world(self, post_dot_digits):
        pool_join = _gentoo_installed_packages_table.\
                join(_gentoo_installed_package_props_table).\
                join(_gentoo_package_pool_table)
        query = select([
                    GentooInstalledPackagesRel.package_id, \
                    GentooPackageString.name, \
                    func.count(GentooInstalledPackagesRel.machine_id.distinct())], \
                from_obj=[pool_join]).\
                where(
                    GentooInstalledPackagePropertiesRel.world == 1).\
                group_by(
                    GentooInstalledPackagesRel.package_id).\
                order_by(
                    func.count(GentooInstalledPackagesRel.machine_id.distinct()).desc(), \
                    GentooPackageString.name).\
                limit(_MAX_INSTALLED_PACKAGES)

        package_id_order = []
        package_dict = {}
        for i in query.execute().fetchall():
            package_id, package_name, machine_count = i

            package_id_order.append(package_id)
            package_dict[package_id] = {
                'name':package_name,
                'absolute_total':machine_count,
                'relative_total':None,
                'slots':{}
            }

        for package_id, package_data in package_dict.items():
            package_data['relative_total'] = self._relative(package_data['absolute_total'], self.gentoo_machines, post_dot_digits)

        return map(package_dict.get, package_id_order)

    def _analyzes_installed_packages_most_installed_all(self, post_dot_digits):
        pool_join = _gentoo_installed_packages_table.\
                join(_gentoo_installed_package_props_table).\
                join(_gentoo_package_pool_table)
        query = select([
                    GentooInstalledPackagesRel.package_id, \
                    GentooPackageString.name, \
                    func.count(GentooInstalledPackagesRel.machine_id.distinct())], \
                from_obj=[pool_join]).\
                group_by(
                    GentooInstalledPackagesRel.package_id).\
                order_by(
                    func.count(GentooInstalledPackagesRel.machine_id.distinct()).desc(), \
                    GentooPackageString.name).\
                limit(_MAX_INSTALLED_PACKAGES)

        package_id_order = []
        package_dict = {}
        for i in query.execute().fetchall():
            package_id, package_name, machine_count = i

            package_id_order.append(package_id)
            package_dict[package_id] = {
                'name':package_name,
                'absolute_total':machine_count,
                'relative_total':None,
                'slots':{}
            }

        pool_join = _gentoo_installed_packages_table.\
                join(_gentoo_installed_package_props_table).\
                join(_gentoo_version_pool_table).\
                join(_gentoo_slot_pool_table)
        query = select([
                    GentooInstalledPackagesRel.package_id, \
                    GentooSlotString.name, \
                    GentooVersionString.name, \
                    func.count(GentooInstalledPackagesRel.machine_id.distinct())], \
                from_obj=[pool_join]).\
                where(
                    GentooInstalledPackagesRel.package_id.in_(package_id_order)).\
                group_by(
                    GentooInstalledPackagesRel.package_id, \
                    GentooInstalledPackagesRel.slot_id, \
                    GentooInstalledPackagePropertiesRel.version_id)
        for i in query.execute().fetchall():
            package_id, slot_name, version_name, machine_count = i
            if slot_name not in package_dict[package_id]['slots']:
                package_dict[package_id]['slots'][slot_name] = {
                    'absolute_total':None,
                    'relative_total':None,
                    'versions':{}
                }
            package_dict[package_id]['slots'][slot_name]['versions'][version_name] = {
                'absolute_total':machine_count,
                'relative_total':None,
            }
            # print ', '.join(map(str, i))

        for package_id, package_data in package_dict.items():
            for slot_name, slot_data in package_data['slots'].items():
                slot_data['absolute_total'] = 0
                for version, version_data in slot_data['versions'].items():
                    slot_data['absolute_total'] = slot_data['absolute_total'] + version_data['absolute_total']
                    version_data['relative_total'] = self._relative(version_data['absolute_total'], self.gentoo_machines, post_dot_digits)
                # TODO reduce version rows to _MAX_INSTALLED_PACKAGE_SLOT_VERSIONS here, keep max entries, accumulate others into "others"
                slot_data['relative_total'] = self._relative(slot_data['absolute_total'], self.gentoo_machines, post_dot_digits)
            # TODO reduce slot rows to _MAX_INSTALLED_PACKAGE_SLOTS here, keep max entries, accumulate others into "others"
            package_data['relative_total'] = self._relative(package_data['absolute_total'], self.gentoo_machines, post_dot_digits)

        return map(package_dict.get, package_id_order)

    def _analyzes_installed_packages_most_unmasked(self, post_dot_digits):
        s = text("""\
                SELECT
                gentoo_installed_packages.package_id AS package_id,
                gentoo_package_pool.name AS package_name,
                SUM(IF(keyword_status = 1, 1, 0)) AS sum_tilde_arch,
                SUM(IF(keyword_status = 2, 1, 0)) AS sum_double_asterisk,
                SUM(unmasked),
                SUM(IF(keyword_status != 0, 1, unmasked)) AS sum_any
                FROM gentoo_installed_packages, gentoo_installed_package_props, gentoo_package_pool
                WHERE
                gentoo_installed_packages.id = gentoo_installed_package_props.installed_package_id AND
                gentoo_package_pool.id = gentoo_installed_packages.package_id
                GROUP BY package_id
                ORDER BY sum_any DESC, package_name ASC
                LIMIT %(limit)d\
                """ % {
                    'limit':_MAX_INSTALLED_PACKAGES
                })
        package_id_order = []
        package_dict = {}
        for i in metadata.bind.execute(s).fetchall():
            package_id, package_name, \
                    tilde_arch_absolute_total, \
                    double_asterisk_absolute_total, \
                    unmask_absolute_total, \
                    any_absolute_total, \
                    = i

            package_id_order.append(package_id)
            package_dict[package_id] = {
                'name':package_name,
                'tilde_arch_absolute_total':tilde_arch_absolute_total,
                'tilde_arch_relative_total':None,
                'double_asterisk_absolute_total':double_asterisk_absolute_total,
                'double_asterisk_relative_total':None,
                'unmask_absolute_total':unmask_absolute_total,
                'unmask_relative_total':None,
                'any_absolute_total':any_absolute_total,
                'any_relative_total':None,
                'slots':{}
            }

        s = text("""
                SELECT
                    gentoo_installed_packages.package_id AS package_id,
                    gentoo_slot_pool.name AS slot_name,
                    gentoo_version_pool.name AS version_name,
                    SUM(IF(keyword_status = 1, 1, 0)) AS sum_tilde_arch,
                    SUM(IF(keyword_status = 2, 1, 0)) AS sum_double_asterisk,
                    SUM(unmasked),
                    SUM(IF(keyword_status != 0, 1, unmasked)) AS sum_any
                FROM
                    gentoo_installed_packages,
                    gentoo_installed_package_props,
                    gentoo_package_pool,
                    gentoo_slot_pool,
                    gentoo_version_pool
                WHERE
                    gentoo_installed_packages.id = gentoo_installed_package_props.installed_package_id AND
                    gentoo_package_pool.id = gentoo_installed_packages.package_id AND
                    gentoo_slot_pool.id = gentoo_installed_packages.slot_id AND
                    gentoo_version_pool.id = gentoo_installed_package_props.version_id AND
                    gentoo_installed_packages.package_id IN (%(package_id)s)
                GROUP BY
                    package_id,
                    slot_id,
                    version_id
                """ % {
                    'package_id':','.join(map(str, package_id_order))
                })
        for i in metadata.bind.execute(s).fetchall():
            package_id, slot_name, version_name, \
                    tilde_arch_absolute_total, \
                    double_asterisk_absolute_total, \
                    unmask_absolute_total, \
                    any_absolute_total, \
                    = i

            if slot_name not in package_dict[package_id]['slots']:
                package_dict[package_id]['slots'][slot_name] = {
                    'tilde_arch_absolute_total':None,
                    'tilde_arch_relative_total':None,
                    'double_asterisk_absolute_total':None,
                    'double_asterisk_relative_total':None,
                    'unmask_absolute_total':None,
                    'unmask_relative_total':None,
                    'any_absolute_total':None,
                    'any_relative_total':None,
                    'versions':{}
                }
            package_dict[package_id]['slots'][slot_name]['versions'][version_name] = {
                'tilde_arch_absolute_total':tilde_arch_absolute_total,
                'tilde_arch_relative_total':None,
                'double_asterisk_absolute_total':double_asterisk_absolute_total,
                'double_asterisk_relative_total':None,
                'unmask_absolute_total':unmask_absolute_total,
                'unmask_relative_total':None,
                'any_absolute_total':any_absolute_total,
                'any_relative_total':None,
            }
            # print ', '.join(map(str, i))

        for package_id, package_data in package_dict.items():
            for slot_name, slot_data in package_data['slots'].items():
                for key in ('tilde_arch_absolute_total', \
                            'double_asterisk_absolute_total', \
                            'unmask_absolute_total', \
                            'any_absolute_total', ):
                    slot_data[key] = 0
                for version, version_data in slot_data['versions'].items():
                    for key in ('tilde_arch_absolute_total', \
                                'double_asterisk_absolute_total', \
                                'unmask_absolute_total', \
                                'any_absolute_total', ):
                        slot_data[key] = slot_data[key] + version_data[key]
                    version_data['tilde_arch_relative_total'] = self._relative(version_data['tilde_arch_absolute_total'], self.gentoo_machines, post_dot_digits)
                    version_data['double_asterisk_relative_total'] = self._relative(version_data['double_asterisk_absolute_total'], self.gentoo_machines, post_dot_digits)
                    version_data['unmask_relative_total'] = self._relative(version_data['unmask_absolute_total'], self.gentoo_machines, post_dot_digits)
                    version_data['any_relative_total'] = self._relative(version_data['any_absolute_total'], self.gentoo_machines, post_dot_digits)
                # TODO reduce version rows to _MAX_INSTALLED_PACKAGE_SLOT_VERSIONS here, keep max entries, accumulate others into "others"
                slot_data['tilde_arch_relative_total'] = self._relative(slot_data['tilde_arch_absolute_total'], self.gentoo_machines, post_dot_digits)
                slot_data['double_asterisk_relative_total'] = self._relative(slot_data['double_asterisk_absolute_total'], self.gentoo_machines, post_dot_digits)
                slot_data['unmask_relative_total'] = self._relative(slot_data['unmask_absolute_total'], self.gentoo_machines, post_dot_digits)
                slot_data['any_relative_total'] = self._relative(slot_data['any_absolute_total'], self.gentoo_machines, post_dot_digits)
            # TODO reduce slot rows to _MAX_INSTALLED_PACKAGE_SLOTS here, keep max entries, accumulate others into "others"
            package_data['tilde_arch_relative_total'] = self._relative(package_data['tilde_arch_absolute_total'], self.gentoo_machines, post_dot_digits)
            package_data['double_asterisk_relative_total'] = self._relative(package_data['double_asterisk_absolute_total'], self.gentoo_machines, post_dot_digits)
            package_data['unmask_relative_total'] = self._relative(package_data['unmask_absolute_total'], self.gentoo_machines, post_dot_digits)
            package_data['any_relative_total'] = self._relative(package_data['any_absolute_total'], self.gentoo_machines, post_dot_digits)

        res = {
            'listed':map(package_dict.get, package_id_order),
            'total':{
                'tilde_arch_absolute_total':self.gentoo_machines,
                'tilde_arch_relative_total':self._relative(self.gentoo_machines, self.gentoo_machines, post_dot_digits),
                'double_asterisk_absolute_total':self.gentoo_machines,
                'double_asterisk_relative_total':self._relative(self.gentoo_machines, self.gentoo_machines, post_dot_digits),
                'unmask_absolute_total':self.gentoo_machines,
                'unmask_relative_total':self._relative(self.gentoo_machines, self.gentoo_machines, post_dot_digits),
                'any_absolute_total':self.gentoo_machines,
                'any_relative_total':self._relative(self.gentoo_machines, self.gentoo_machines, post_dot_digits),
            }
        }
        return res

    def _analyzes_installed_packages(self):
        if _MAX_INSTALLED_PACKAGES >= 50:
            post_dot_digits = 2
        else:
            post_dot_digits = 1

        most_installed_world = self._analyzes_installed_packages_most_installed_world(post_dot_digits)
        most_installed_all = self._analyzes_installed_packages_most_installed_all(post_dot_digits)
        most_unmasked = self._analyzes_installed_packages_most_unmasked(post_dot_digits)

        res = {
            'most_installed_world':{
                'listed':most_installed_world,
                'total':{
                    'absolute_total':self.gentoo_machines,
                    'relative_total':self._relative(self.gentoo_machines, self.gentoo_machines, post_dot_digits),
                }
            },
            'most_installed_all':{
                'listed':most_installed_all,
                'total':{
                    'absolute_total':self.gentoo_machines,
                    'relative_total':self._relative(self.gentoo_machines, self.gentoo_machines, post_dot_digits),
                }
            },
            'most_unmasked':most_unmasked
        }
        return res

    def _analyzes_call_flags(self):
        def make_row(absolute, post_dot_digits, label=None):
            res = {
                'absolute':absolute,
                'relative':self._relative(absolute, self.gentoo_machines, post_dot_digits),
            }
            if label != None:
                res['label'] = label
            return res

        res = {}
        for call_flag_class_upper in ('CFLAGS', 'CXXFLAGS', 'LDFLAGS', 'MAKEOPTS'):
            final_rows = []
            try:
                call_flag_class_object = self.session.query(GentooCallFlagClassString).filter_by(name=call_flag_class_upper).one()
            except sqlalchemy.orm.exc.NoResultFound:
                total_entry_count = 0
                others = 0
                post_dot_digits = 1
            else:
                call_flag_class_id = call_flag_class_object.id

                pool_join = _gentoo_call_flags_table.join(_gentoo_call_flag_pool_table)
                total_entry_count = self.session.query(GentooCallFlagRel).filter_by(call_flag_class_id=call_flag_class_id).count()
                query = select([GentooCallFlagString.name, func.count(GentooCallFlagRel.machine_id)], \
                        from_obj=[pool_join]).where(GentooCallFlagRel.call_flag_class_id == call_flag_class_id).\
                        group_by(GentooCallFlagRel.call_flag_id).order_by(\
                        func.count(GentooCallFlagRel.machine_id).desc(), GentooCallFlagString.name).limit(_MAX_CALL_FLAGS)
                if _MAX_CALL_FLAGS >= 50:
                    post_dot_digits = 2
                else:
                    post_dot_digits = 1

                others = total_entry_count
                for i in query.execute().fetchall():
                    label, absolute = i
                    others = others - absolute
                    final_rows.append(make_row(absolute, post_dot_digits, label))
                if others < 0:
                    others = 0

            res[call_flag_class_upper.lower()] = {
                'listed':final_rows,
                'others':[make_row(others, post_dot_digits)],
                'total':[make_row(total_entry_count, post_dot_digits)],
            }
        return res

    # TODO testing
    def _explain_time_delta(self, d):
        def numerus(number):
            if number == 1:
                return ''
            else:
                return 's'

        def format_seconds(s):
            return '%d second%s' % (seconds, numerus(seconds))

        words = []
        if d.days > 0:
            words.append('%d day%s' % (d.days, numerus(d.days)))
        seconds = d.seconds
        hours = seconds / 3600
        seconds = seconds - 3600 * hours
        minutes = seconds / 60
        seconds = seconds - 60 * minutes
        if hours > 0:
            words.append('%d hour%s' % (hours, numerus(hours)))
        if minutes > 0:
            words.append('%d minute%s' % (minutes, numerus(minutes)))

        if words:
            words.append(format_seconds(seconds))
            return ', '.join(words[:-1]) + ' and ' + words[-1]
        else:
            if seconds == 0:
                return 'less than 1 second'
            else:
                return format_seconds(seconds)

    def gather(self):
        report_begun = datetime.datetime.utcnow()
        query = select([func.count(GentooPrivacyMetricRel.machine_id.distinct())])
        self.gentoo_machines = max(1, self.session.execute(query).fetchall()[0][0])
        del query

        simple_stuff = self._analyze_simple_stuff()
        global_use_flags = self._analyze_global_use_flags()
        archs = self._analyze_archs()
        call_flags = self._analyzes_call_flags()
        package_mask = self._analyzes_package_mask()
        repos = self._analyzes_repos()
        installed_packages = self._analyzes_installed_packages()

        report_finished = datetime.datetime.utcnow()
        generation_duration = self._explain_time_delta(\
                report_finished - report_begun)
        data = {
            'generation_time':datetime.datetime.strftime(\
                    report_finished, "%Y-%m-%d %H:%S UTC"),
            'generation_duration':generation_duration,
            'archs':archs,
            'call_flags':call_flags,
            'package_mask':package_mask,
            'global_use_flags':global_use_flags,
            'repos':repos,
            'installed_packages':installed_packages,
        }
        for k, v in simple_stuff.items():
            if k in data:
                raise Exception('Fatal key collision')
            data[k] = v
        self._data = data

    def data(self):
        return self._data


def gentoo_data_tree(session):
    gentoo_reporter = GentooReporter(session)
    gentoo_reporter.gather()
    return gentoo_reporter.data()
