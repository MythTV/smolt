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
from overlays import Overlays

class PackageMask:
    def __init__(self):
        self._collect()

    def _collect(self):
        self._cp_to_atoms = defaultdict(list)
        self._total_count = 0
        self._secret_count = 0
        abs_user_config = os.path.join(
            portage.settings["PORTAGE_CONFIGROOT"],
            portage.USER_CONFIG_PATH.lstrip(os.path.sep))
        for x in portage.grabfile_package(
                os.path.join(abs_user_config, "package.mask"), recursive = 1):
            self._total_count = self._total_count + 1
            cp = portage.dep_getkey(x)
            if Overlays().is_secret_package(cp):
                self._secret_count = self._secret_count + 1
                continue
            self._cp_to_atoms[cp].append(x)

    def total_count(self):
        return self._total_count

    def secret_count(self):
        return self._secret_count

    def known_count(self):
        return self.total_count() - self.secret_count()

    def dump(self):
        print 'package.mask:'
        for k, v in self._cp_to_atoms.items():
            print '  %s: %s' % (k, v)
        print
        print 'Total: ' + str(self.total_count())
        print '  Known: ' + str(self.known_count())
        print '  Secret: ' + str(self.secret_count())

if __name__ == '__main__':
    package_mask = PackageMask()
    package_mask.dump()
