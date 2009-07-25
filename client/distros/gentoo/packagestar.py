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

from collections import defaultdict
import os
import portage
from packageprivacy import is_private_package_atom

class _PackageStar:
    def __init__(self):
        pass

    def _init(self, section, privacy_filter):
        self._section = section
        self._privacy_filter = privacy_filter
        self._collect()

    def _locations(self):
        return [os.path.join(
            portage.settings["PORTAGE_CONFIGROOT"],
            portage.USER_CONFIG_PATH.lstrip(os.path.sep))]

    def _collect(self):
        self._non_private_cp_to_atoms = defaultdict(list)
        self._private_cp_to_atoms = defaultdict(list)
        self._total_count = 0
        self._private_count = 0
        for location in self._locations():
            for x in portage.grabfile_package(
                    os.path.join(location, self._section), recursive = 1):
                self._total_count = self._total_count + 1
                cp = portage.dep_getkey(x)
                if self._privacy_filter and is_private_package_atom(cp):
                    self._private_count = self._private_count + 1
                    dict_ref = self._private_cp_to_atoms
                else:
                    dict_ref = self._non_private_cp_to_atoms

                merge_with = set([x])
                if cp in dict_ref:
                    dict_ref[cp] = dict_ref[cp].union(merge_with)
                else:
                    dict_ref[cp] = merge_with

    def total_count(self):
        return self._total_count

    def private_count(self):
        return self._private_count

    def known_count(self):
        return self.total_count() - self.private_count()

    def _hits(self, cpv, dict_ref):
        cp = portage.dep_getkey(cpv)
        if cp not in dict_ref:
            return False
        test_atom = '=' + cpv
        for a in dict_ref[cp]:
            if portage.dep.get_operator(a) == None:
                return True
            elif not not portage.dep.match_from_list(test_atom, [a]):
                return True
        return False

    def hits(self, cpv):
        for dict_ref in (self._non_private_cp_to_atoms, self._private_cp_to_atoms):
            if self._hits(cpv, dict_ref):
                return True
        return False

    def serialize(self):
        res = {}
        for cp, atoms in self._non_private_cp_to_atoms.items():
            res[cp] = sorted(atoms)
        return res

    def dump_html(self, lines):
        lines.append('<h2>%s</h2>' % self._section)
        lines.append('<ul>')
        for atoms in self.serialize().values():
            for v in atoms:
                lines.append('<li>%s</li>' % v)
        lines.append('</ul>')

    def dump(self):
        print '%s:' % (self._section)
        for k, v in self._non_private_cp_to_atoms.items():
            print '  %s: %s' % (k, v)
        print
        print '  Total: ' + str(self.total_count())
        print '    Known: ' + str(self.known_count())
        print '    Private: ' + str(self.private_count())
        print


class _PackageMask(_PackageStar):
    def __init__(self):
        self._init('package.mask', privacy_filter=True)


class _PackageUnmask(_PackageStar):
    def __init__(self):
        self._init('package.unmask', privacy_filter=True)


class _ProfilePackageMask(_PackageStar):
    def __init__(self):
        self._init('package.mask', privacy_filter=False)

    def _locations(self):
        main_tree_profiles = [os.path.join(portage.settings["PORTDIR"],
            "profiles")] + portage.settings.profiles # TODO break potential
        overlay_profiles = [os.path.join(e, "profiles") for e in \
            portage.settings["PORTDIR_OVERLAY"].split()]
        return[e for e in main_tree_profiles + overlay_profiles if \
            os.path.isdir(e)]


_package_unmask_instance = None
def PackageUnmask():
    """
    Simple singleton wrapper around _PackageUnmask class
    """
    global _package_unmask_instance
    if _package_unmask_instance == None:
        _package_unmask_instance = _PackageUnmask()
    return _package_unmask_instance


_package_mask_instance = None
def PackageMask():
    """
    Simple singleton wrapper around _PackageMask class
    """
    global _package_mask_instance
    if _package_mask_instance == None:
        _package_mask_instance = _PackageMask()
    return _package_mask_instance


_profile_package_mask_instance = None
def ProfilePackageMask():
    """
    Simple singleton wrapper around _ProfilePackageMask class
    """
    global _profile_package_mask_instance
    if _profile_package_mask_instance == None:
        _profile_package_mask_instance = _ProfilePackageMask()
    return _profile_package_mask_instance


if __name__ == '__main__':
    package_mask = PackageMask()
    package_mask.dump()
    package_unmask = PackageUnmask()
    package_unmask.dump()
    profile_package_mask = ProfilePackageMask()
    profile_package_mask.dump()
