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
from systemprofile import SystemProfile

import os
import sys
sys.path.append(os.path.join(sys.path[0], '..', '..'))
import distros.shared.html as html

class Trivials:
    def __init__(self):
        self._trivials = {}

        self._trivial_scalars = {}
        for k in ('ARCH', 'CHOST'):
            self._trivial_scalars[k] = portage.settings[k].strip()
            self._trivials[k] = self._trivial_scalars[k]

        self._trivial_scalars['system_profile'] = SystemProfile().get()
        self._trivials['system_profile'] = self._trivial_scalars['system_profile']

        self._trivial_vectors = {}
        for k in ('FEATURES',):
            self._trivial_vectors[k] = portage.settings[k].split(' ')
            self._trivials[k] = self._trivial_vectors[k]

        self._trivial_vectors['ACCEPT_KEYWORDS'] = \
            self._accept_keywords()
        self._trivials['ACCEPT_KEYWORDS'] = \
            self._trivial_vectors['ACCEPT_KEYWORDS']

    def _accept_keywords(self):
        # Let '~arch' kill 'arch' so we don't get both
        list = portage.settings['ACCEPT_KEYWORDS'].split(' ')
        unstable = set(e for e in list if e.startswith('~'))
        return [e for e in list if not ('~' + e) in unstable]

    def serialize(self):
        return self._trivials

    def dump_html(self, lines):
        lines.append('<h2>General</h2>')
        key_data = {
            'ARCH':'ARCH',
            'CHOST':'CHOST',
            'ACCEPT_KEYWORDS':'ACCEPT_KEYWORDS',
            'system_profile':'System Profile',
        }
        for k, label in sorted(key_data.items()):
            v = self._trivials[k]
            lines.append('<dl>')
            lines.append('<dt>%s</dt>' % html.escape(label))
            if type(v).__name__ == 'list':
                lines.append('<dd>%s</dd>' % html.escape(', '.join(v)))
            else:
                lines.append('<dd>%s</dd>' % html.escape(v))
            lines.append('</dl>')

        lines.append('<h2>Features</h2>')
        lines.append('<ul>')
        for i in sorted(self._trivials['FEATURES']):
            lines.append('<li>%s</li>' % html.escape(i))
        lines.append('</ul>')

    def dump_rst(self, lines):
        lines.append('General')
        lines.append('-----------------------------')
        key_data = {
            'ARCH':'ARCH',
            'CHOST':'CHOST',
            'ACCEPT_KEYWORDS':'ACCEPT_KEYWORDS',
            'system_profile':'System Profile',
        }
        for k, label in sorted(key_data.items()):
            v = self._trivials[k]
            lines.append(label)
            if type(v).__name__ == 'list':
                lines.append('  %s' % ', '.join(v))
            else:
                lines.append('  %s' % v)
            lines.append('')

        lines.append('Features')
        lines.append('-----------------------------')
        for i in sorted(self._trivials['FEATURES']):
            lines.append('- %s' % i)


    def _dump(self):
        lines = []
        self.dump_rst(lines)
        print '\n'.join(lines)
        print

    """
    def dump(self):
        print 'Trivial scalars:'
        for k, v in self._trivial_scalars.items():
            print '  %s: %s' % (k, v)
        print 'Trivial vectors:'
        for k, v in self._trivial_vectors.items():
            print '  %s: %s' % (k, v)
        print
    """

if __name__ == '__main__':
    trivials = Trivials()
    trivials._dump()
