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

from portage.dbapi.vartree import vartree
from portage.versions import catpkgsplit
from overlays import Overlays
from globaluseflags import GlobalUseFlags

class InstalledPackages:
    def __init__(self):
        self._cpv_flag_list = []
        var_tree = vartree()
        installed_cpvs = var_tree.getallcpv()
        for cpv in installed_cpvs:
            if Overlays().is_secret_package(cpv):
                continue
            use, iuse = var_tree.dbapi.aux_get(cpv, ["USE", "IUSE"])
            use_flags = GlobalUseFlags()
            flags = set(e for e in use.split() if use_flags.is_known(e)) & \
                set(x.lstrip("+-") for x in iuse.split() if use_flags.is_known(x))
            self._cpv_flag_list.append(self._make_package_info(cpv, flags))

    def _make_package_info(self, cpv, flags):
        cat, pkg, ver, rev = catpkgsplit(cpv)
        return ["%s/%s" % (cat, pkg), "%s-%s" % (ver, rev), sorted(flags)]

    def dump(self):
        print 'Packages:'
        for list in self._cpv_flag_list:
            print list

if __name__ == '__main__':
    installed_packages = InstalledPackages()
    installed_packages.dump()
