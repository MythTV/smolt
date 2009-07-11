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
import os
import sets
from tools.maintreedir import main_tree_dir

class GlobalUseFlags:
    def __init__(self):
        self._fill_use_flags()

    def _registered_global_use_flags(self):
        try:
            f = open(os.path.join(main_tree_dir(), 'profiles', 'use.desc'), 'r')
            lines = [re.sub('^([^ ]+) - .*\\n', '\\1', l) for l in
                    f.readlines() if re.match('^[^ ]+ - ', l)]
            f.close()
            return set(lines)
        except IOError:
            return set()

    def _registered_local_use_flags(self):
        try:
            f = open(os.path.join(main_tree_dir(), 'profiles',
                'use.local.desc'), 'r')
            lines = [re.sub('^[^ :]+:([^ ]+) - .*\\n', '\\1', l) for l in
                    f.readlines() if re.match('^[^ :]+:[^ ]+ - ', l)]
            f.close()
            return set(lines)
        except IOError:
            return set()

    def _expanded_use_flags(self):
        use_flags = []
        expand_desc_dir = os.path.join(main_tree_dir(), 'profiles', 'desc')
        try:
            expand_list = os.listdir(expand_desc_dir)
        except OSError:
            pass
        else:
            for desc_filename in expand_list:
                if not desc_filename.endswith('.desc'):
                    continue
                use_prefix = desc_filename[:-5].lower() + '_'
                for line in portage.grabfile(os.path.join(
                        expand_desc_dir, desc_filename)):
                    x = line.split()
                    if x:
                        use_flags.append(use_prefix + x[0])
        return set(use_flags)

    def _auto_use_flags(self):
        return set(portage.grabfile(os.path.join(main_tree_dir(), 'profiles',
            'arch.list')))

    def _fill_use_flags(self):
        active_use_flags = \
                [e.lstrip("+") for e in portage.settings['USE'].split(' ')]
        self._total_count = \
                len(active_use_flags)

        # Filter our secret use flags
        registered_global_use_flags = self._registered_global_use_flags()
        non_secret_space = registered_global_use_flags.union(
                self._registered_local_use_flags()).union(
                self._expanded_use_flags()).union(
                self._auto_use_flags())
        def is_non_secret(x):
            try:
                if (x in non_secret_space) or ("-" + x in non_secret_space):
                    return True
                else:
                    return False
            except KeyError:
                return False
        self._global_use_flags = set([e for e in active_use_flags
                if is_non_secret(e)])
        self._secret_count = \
                self._total_count - len(self._global_use_flags)

    def get(self):
        return self._global_use_flags

    def total_count(self):
        return self._total_count

    def secret_count(self):
        return self._secret_count

    def known_count(self):
        return self.total_count() - self.secret_count()

    def is_known(self, flag):
        return flag in self._global_use_flags

    def dump(self):
        print 'Global use flags:'
        print sorted(self.get())
        print '  Total: ' + str(self.total_count())
        print '    Known: ' + str(self.known_count())
        print '    Secret: ' + str(self.secret_count())
        print

if __name__ == '__main__':
    globaluseflags = GlobalUseFlags()
    globaluseflags.dump()
