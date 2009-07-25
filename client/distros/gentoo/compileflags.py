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

import re
import portage
from makeopts import MakeOpts

import os
import sys
sys.path.append(os.path.join(sys.path[0], '..', '..'))
import distros.shared.html as html

SHORT_PARA_PATTERN = '-[XxAloDUubVIG]\\s+\\S+|-[^-]\\S+'
LONG_PARA_PATTERN = '--param\\s+\\S+=\\S+|--\\S+|--\\S+=\\S+'
PARA_PATTERN = re.compile('(%s|%s)\\b' % (SHORT_PARA_PATTERN, LONG_PARA_PATTERN))
LINKER_FLAG_LIST_PATTERN = re.compile('-Wl,[^,]*,')

class CompileFlags:
    def __init__(self):
        self._cflags = self._parse(portage.settings['CFLAGS'])
        self._cxxflags = self._parse(portage.settings['CXXFLAGS'])
        self._ldflags = self._parse(portage.settings['LDFLAGS'])

    def _parse(self, flags):
        list = []
        for m in re.finditer(PARA_PATTERN, flags):
            text = re.sub('\\s{2,}', ' ', m.group()) # Normalize whitespace
            if re.match(LINKER_FLAG_LIST_PATTERN, text):
                # "-Wl,foo,bar" --> "-Wl,foo" "-Wl,bar"
                split_linker_flags = ['-Wl,%s' % e for e in text.split(',')[1:]]
                list.extend(split_linker_flags)
            else:
                list.append(text)
        return list

    def get_cflags(self):
        return self._cflags

    def get_cxxflags(self):
        return self._cxxflags

    def get_ldflags(self):
        return self._ldflags

    def serialize(self):
        res = {
            'CFLAGS':self._cflags,
            'CXXFLAGS':self._cxxflags,
            'LDFLAGS':self._ldflags,
            'MAKEOPTS':MakeOpts().serialize(),
        }
        return res

    def dump_html(self, lines):
        lines.append('<h2>Compile flags</h2>')
        for group, values in sorted(self.serialize().items()):
            lines.append('<h3>%s</h3>' % html.escape(group))
            lines.append('<ul>')
            for v in values:
                lines.append('<li>%s</li>' % html.escape(v))
            lines.append('</ul>')

    def dump(self):
        print 'Compile flags:'
        print '  CFLAGS: ' + str(self.get_cflags())
        print '  CXXFLAGS: ' + str(self.get_cxxflags())
        print '  LDFLAGS: ' + str(self.get_ldflags())
        print

if __name__ == '__main__':
    compileflags = CompileFlags()
    compileflags.dump()

"""
Samples
-Os -pipe -march=armv6j -mtune=arm1136jf-s -mfpu=vfp --param ggc-min-expand=0 --param ggc-min-heapsize=65536"
-march=k8 -O2 -pipe -ggdb -Wall
-Wl,-O1 -Wl,--hash-style=gnu,--enable-new-dtags,--as-needed
"""
