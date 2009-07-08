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
import re
import sets
from tools.maintreedir import main_tree_dir

class GlobalUseFlags:
    def __init__(self):
        self._fill_use_flags()

    def _registered_global_use_flags(self):
        try:
            f = open('%s/profiles/use.desc' % main_tree_dir(), 'r')
            lines = [re.sub('^([^ ]+) - .*\\n', '\\1', l) for l in
                    f.readlines() if re.match('^[^ ]+ - ', l)]
            f.close()
            return set(lines)
        except IOError:
            return set()

    def _registered_local_use_flags(self):
        try:
            f = open('%s/profiles/use.local.desc' % main_tree_dir(), 'r')
            lines = [re.sub('^[^ :]+:([^ ]+) - .*\\n', '\\1', l) for l in
                    f.readlines() if re.match('^[^ :]+:[^ ]+ - ', l)]
            f.close()
            return set(lines)
        except IOError:
            return set()

    def _fill_use_flags(self):
        # Obtain all USE_EXPAND values:
        # for i in $(grep -h '^\(# *\)\?[^ ]\+=' /etc/make.{conf,globals} \
        #     $(find /usr/portage/profiles/ -name make.defaults) \
        #   | sed -e 's|^# *||' | grep USE_EXPAND \
        #   | sed -e 's|^USE_EXPAND\(_HIDDEN\)\?="||' -e 's|"$||') ; do \
        #   echo $i ; done | sed 's|^-||' | sort -u

        # Filter out USE_EXPAND stuff, e.g. kernel_linux, userland_gnu, ...
        use_expand = [e.lower() + "_" for e in
                portage.settings['USE_EXPAND'].split(' ')
                if not e.startswith('-')]
        arch = portage.settings['ARCH']
        def is_expanded(use_flag):
            if use_flag == arch:
                return True
            for prefix in use_expand:
                if use_flag.startswith(prefix):
                    return True
            return False
        non_expand_use_flags = \
                [e for e in portage.settings['USE'].split(' ')
                if not is_expanded(e)]
        self._total_count = \
                len(non_expand_use_flags)

        # Filter our private use flags
        registered_global_use_flags = self._registered_global_use_flags()
        non_private_space = registered_global_use_flags.union(
                self._registered_local_use_flags())
        def is_non_private(x):
            try:
                if x in non_private_space:
                    return True
                else:
                    return False
            except KeyError:
                return False
        self._global_use_flags = set([e for e in non_expand_use_flags
                if is_non_private(e)])
        self._secret_count = \
                self._total_count - len(self._global_use_flags)

        # Partition into global and local, prefer global in doubt
        # Check against global global set is faster as it's much smaller
        self._global_global_count = 0
        self._local_global_count = 0
        for use_flag in self._global_use_flags:
            if use_flag in registered_global_use_flags:
                self._global_global_count = self._global_global_count + 1
            else:
                self._local_global_count = self._local_global_count + 1

    def get(self):
        return self._global_use_flags

    def total_count(self):
        return self._total_count

    def secret_count(self):
        return self._secret_count

    def known_count_global_global(self):
        return self._global_global_count

    def known_count_local_global(self):
        return self._local_global_count

    def is_known(self, flag):
        return flag in self._global_use_flags

    def dump(self):
        print 'Global use flags: ' + str(self.get())
        print 'Total: ' + str(self.total_count())
        print 'Known global global: ' + str(self.known_count_global_global())
        print 'Known local global: ' + str(self.known_count_local_global())
        print 'Secret: ' + str(self.secret_count())

if __name__ == '__main__':
    globaluseflags = GlobalUseFlags()
    globaluseflags.dump()
