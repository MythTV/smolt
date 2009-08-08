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
from tools.maintreedir import main_tree_dir

import os
import sys
sys.path.append(os.path.join(sys.path[0], '..', '..'))
import distros.shared.html as html

try:
    set
except NameError:
    from sets import Set as set  # Python 2.3 fallback


def _flatten_dict_tree(dict_tree):
    def process_compressables(compressables, res):
        if len(compressables) > 1:
            res.append((k + '_' + '{' + ','.join(s for (s, d) in compressables) + '}', 1))
        else:
            res.append((k + '_' + compressables[0][0], 1))

    res = []
    for k in sorted(dict_tree.keys()):
        flat = _flatten_dict_tree(dict_tree[k])
        if not flat:
            res.append((k, 0))
        else:
            if len(flat) > 1:
                compressables = []
                for (s, d) in sorted(flat):
                    if d > 0:
                        if compressables:
                            process_compressables(compressables, res)
                            compressables = []
                        res.append((k + '_' + s, d))
                    else:
                        compressables.append((s, d))
                if compressables:
                    process_compressables(compressables, res)
            else:
                res.append((k + '_' + flat[0][0], flat[0][1]))
    return res

def compress_use_flags(flag_list):
    # Convert to tree
    dict_tree = {}
    for f in flag_list:
        parts = f.split('_')
        d = dict_tree
        for i, v in enumerate(parts):
            if v not in d:
                d[v] = {}
            d = d[v]

    # Flatten back
    return [s for (s, d) in _flatten_dict_tree(dict_tree)]


class _GlobalUseFlags:
    def __init__(self):
        self._fill_use_flags()

    def _registered_global_use_flags(self):
        global_line_sub = re.compile('^([^ ]+) - .*\\n')
        global_line_filter = re.compile('^[^ ]+ - ')
        try:
            f = open(os.path.join(main_tree_dir(), 'profiles', 'use.desc'), 'r')
            lines = [global_line_sub.sub('\\1', l) for l in
                    f.readlines() if global_line_filter.match(l)]
            f.close()
            return set(lines)
        except IOError:
            return set()

    def _registered_local_use_flags(self):
        local_line_sub = re.compile('^[^ :]+:([^ ]+) - .*\\n')
        local_line_filter = re.compile('^[^ :]+:[^ ]+ - ')
        try:
            f = open(os.path.join(main_tree_dir(), 'profiles',
                'use.local.desc'), 'r')
            lines = [local_line_sub.sub('\\1', l) for l in
                    f.readlines() if local_line_filter.match(l)]
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

        # Filter our private use flags
        self._non_private_space = self._registered_global_use_flags().union(
                self._registered_local_use_flags()).union(
                self._expanded_use_flags()).union(
                self._auto_use_flags())

        def is_non_private(x):
            try:
                if (x in self._non_private_space) or \
                        ("-" + x in self._non_private_space):
                    return True
                else:
                    return False
            except KeyError:
                return False
        self._global_use_flags = set([e for e in active_use_flags
                if is_non_private(e)])
        self._private_count = \
                self._total_count - len(self._global_use_flags)

    def get(self):
        return self._global_use_flags

    def total_count(self):
        return self._total_count

    def private_count(self):
        return self._private_count

    def known_count(self):
        return self.total_count() - self.private_count()

    def is_known(self, flag):
        return flag in self._non_private_space

    def serialize(self):
        return sorted(self._global_use_flags)

    def dump_html(self, lines):
        lines.append('<h2>Global use flags</h2>')
        lines.append('<p>')
        lines.append(html.escape(', '.join(sorted(self._global_use_flags))))
        lines.append('</p>')

    def dump_rst(self, lines):
        lines.append('Global use flags')
        lines.append('-----------------------------')
        lines.append('  '.join(compress_use_flags(self._global_use_flags)))

    def _dump(self):
        lines = []
        self.dump_rst(lines)
        print '\n'.join(lines)
        print

    """
    def dump(self):
        print 'Global use flags:'
        print sorted(self.get())
        print '  Total: ' + str(self.total_count())
        print '    Known: ' + str(self.known_count())
        print '    Private: ' + str(self.private_count())
        print
    """


_global_use_flags_instance = None
def GlobalUseFlags():
    """
    Simple singleton wrapper around _GlobalUseFlags class
    """
    global _global_use_flags_instance
    if _global_use_flags_instance == None:
        _global_use_flags_instance = _GlobalUseFlags()
    return _global_use_flags_instance


if __name__ == '__main__':
    global_use_flags = GlobalUseFlags()
    global_use_flags._dump()
