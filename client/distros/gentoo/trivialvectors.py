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

import portage

class TrivialVectors:
    def __init__(self):
        self._trivial_scalars = {}
        for k in ('ACCEPT_KEYWORDS', 'FEATURES'):
            self._trivial_scalars[k] = portage.settings[k].split(' ')

    def get(self):
        return self._trivial_scalars

    def dump(self):
        print 'Trivial vectors:'
        for k, v in self._trivial_scalars.items():
            print '  %s: %s' % (k, v)
        print

if __name__ == '__main__':
    TrivialVectors = TrivialVectors()
    TrivialVectors.dump()
