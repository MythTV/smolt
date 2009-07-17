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
        self._trivial_vectors = {}
        for k in ('FEATURES',):
            self._trivial_vectors[k] = portage.settings[k].split(' ')

        self._trivial_vectors['ACCEPT_KEYWORDS'] = \
            self._accept_keywords()

    def _accept_keywords(self):
        # Let '~arch' kill 'arch' so we don't get both
        list = portage.settings['ACCEPT_KEYWORDS'].split(' ')
        unstable = set(e for e in list if e.startswith('~'))
        return [e for e in list if not ('~' + e) in unstable]

    def get(self):
        return self._trivial_vectors

    def serialize(self):
        return self._trivial_vectors

    def dump(self):
        print 'Trivial vectors:'
        for k, v in self._trivial_vectors.items():
            print '  %s: %s' % (k, v)
        print

if __name__ == '__main__':
    TrivialVectors = TrivialVectors()
    TrivialVectors.dump()
