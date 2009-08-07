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
from portage.dbapi.vartree import vartree
from portage.versions import catpkgsplit
from overlays import Overlays
from globaluseflags import GlobalUseFlags, compress_use_flags
from worldset import WorldSet
from packagestar import PackageMask, PackageUnmask, ProfilePackageMask
from packageprivacy import is_private_package_atom

import os
import sys
sys.path.append(os.path.join(sys.path[0], '..', '..'))
import distros.shared.html as html

class InstalledPackages:
    def __init__(self, debug=False,
            cb_enter=None, cb_done=None):
        self._cpv_flag_list = []
        var_tree = vartree()
        installed_cpvs = var_tree.getallcpv()  # TODO upstream plans rename?
        self._total_count = len(installed_cpvs)
        self._private_count = 0
        i = 0
        for cpv in sorted(installed_cpvs):
            i = i + 1
            if cb_enter:
                cb_enter(cpv, i, self._total_count)
            entry = self._process(var_tree, cpv, debug=debug)
            if entry:
                self._cpv_flag_list.append(entry)
            else:
                self._private_count = self._private_count + 1
        if cb_done:
            cb_done()

    def _keyword_status(self, ARCH, ACCEPT_KEYWORDS, KEYWORDS):
        k = set(KEYWORDS.split(' '))
        if ARCH in k:
            return ''
        TILDE_ARCH = '~' + ARCH
        if TILDE_ARCH in k:
            ak = set(ACCEPT_KEYWORDS.split(' '))
            if TILDE_ARCH in ak:
                return ''
            else:
                return '~arch'
        else:
            return '**'

    def _process(self, var_tree, cpv, debug=False):
        cat, pkg, ver, rev = catpkgsplit(cpv)
        package_name = "%s/%s" % (cat, pkg)
        if rev == 'r0':
            version_revision = ver
        else:
            version_revision = "%s-%s" % (ver, rev)

        SLOT, KEYWORDS, repository, IUSE, USE = \
            var_tree.dbapi.aux_get(cpv, ['SLOT', 'KEYWORDS', 'repository',
            'IUSE', 'USE'])

        # Perform privacy check and filtering
        installed_from = [repository, ]
        if is_private_package_atom('=' + cpv, installed_from=installed_from,
                debug=debug):
            return None
        repository = installed_from[0]

        ACCEPT_KEYWORDS = portage.settings['ACCEPT_KEYWORDS']
        ARCH = portage.settings['ARCH']
        keyword_status = self._keyword_status(ARCH, ACCEPT_KEYWORDS, KEYWORDS)

        unmasked = PackageUnmask().hits(cpv)
        # A package that is (1) installed and (2) not unmasked
        # cannot be masked so we skip the next line's checks
        masked = unmasked and (PackageMask().hits(cpv) or \
            ProfilePackageMask().hits(cpv))

        # World set test
        if SLOT != '0':
            world_set_test = '%s/%s:%s' % (cat, pkg, SLOT)
        else:
            world_set_test = '%s/%s' % (cat, pkg)
        is_in_world = world_set_test in WorldSet().get()

        # Use flags
        use_flags = GlobalUseFlags()
        package_use_set = set(e for e in USE.split() if use_flags.is_known(e))
        package_iuse_set = set(x.lstrip("+-") for x in IUSE.split() if use_flags.is_known(x))
        enabled_flags = package_use_set & package_iuse_set
        disabled_flags = package_iuse_set - package_use_set
        package_flags = sorted(enabled_flags) + ['-' + e for e in sorted(disabled_flags)]
        entry = [package_name, version_revision, SLOT, keyword_status,
            masked, unmasked, is_in_world, repository, package_flags]
        return entry

    def total_count(self):
        return self._total_count

    def private_count(self):
        return self._private_count

    def known_count(self):
        return len(self._cpv_flag_list)

    def serialize(self):
        return self._cpv_flag_list

    def dump_html(self, lines):
        lines.append('<h2>Installed packages</h2>')
        lines.append('<table border="1" cellspacing="1" cellpadding="4">')
        lines.append('<tr>')
        for i in ('Package', 'Version', 'Slot', 'Keyword', 'Masked', 'Unmasked', 'World', 'Tree', 'Use flags'):
            lines.append('<th>%s</th>' % i)
        lines.append('</tr>')
        for list in self._cpv_flag_list:
            package_name, version_revision, SLOT, keyword_status, \
                masked, unmasked, is_in_world, repository, sorted_flags_list = \
                list

            lines.append('<tr>')
            for i in (package_name, version_revision):
                lines.append('<td>%s</td>' % html.escape(i))
            for i in (SLOT, ):
                if i == '0':  # Hide default slot
                    v = ''
                else:
                    v = i
                lines.append('<td>%s</td>' % html.escape(v))
            for i in (keyword_status, ):
                lines.append('<td>%s</td>' % html.escape(i))
            for i in (masked, unmasked, is_in_world):
                v = i and 'X' or '&nbsp;'  # Hide False
                lines.append('<td>%s</td>' % v)
            for i in (repository, ):
                lines.append('<td>%s</td>' % html.escape(i))
            lines.append('<td>%s</td>' % html.escape(', '.join(sorted_flags_list)))
            lines.append('</tr>')
        lines.append('</table>')

    def dump_rst(self, lines):
        lines.append('Installed packages')
        lines.append('-----------------------------')
        for list in self._cpv_flag_list:
            package_name, version_revision, SLOT, keyword_status, \
                masked, unmasked, is_in_world, repository, sorted_flags_list = \
                list

            lines.append('- %s-%s' % (package_name, version_revision))

            if SLOT != '0':  # Hide default slot
                lines.append('  - Slot: %s' % (SLOT))
            if keyword_status:
                lines.append('  - Keyword status: %s' % keyword_status)

            tag_names = ('masked', 'unmasked', 'world')
            values = (masked, unmasked, is_in_world)
            tags = []
            for i, v in enumerate(values):
                if v:
                    tags.append(tag_names[i])
            if tags:
                lines.append('  - Tags: %s' % ', '.join(tags))

            if repository:
                lines.append('  - Repository: %s' % (repository))
            if sorted_flags_list:
                flag_list = [x.startswith('-') and x or ('+' + x) for x in compress_use_flags(sorted_flags_list)]
                if len(flag_list) > 1:
                    f = '{%s}' % (','.join(flag_list))
                else:
                    f = flag_list[0]
                lines.append('  - Flags: %s' % f)

    def _dump(self):
        lines = []
        self.dump_rst(lines)
        print '\n'.join(lines)
        print

    """
    def dump(self):
        print 'Installed packages:'
        for list in self._cpv_flag_list:
            package_name, version_revision, SLOT, keyword_status, \
                masked, unmasked, is_in_world, repository, sorted_flags_list = \
                list
            tags = [e for e in [
                masked and 'MASKED' or '',
                unmasked and 'UNMASKED' or '',
                is_in_world and 'WORLD' or ''] if e]
            print [package_name, version_revision, SLOT, keyword_status,
                tags, repository, sorted_flags_list]
        print
        print '  Total: ' + str(self.total_count())
        print '    Known: ' + str(self.known_count())
        print '    Private: ' + str(self.private_count())
        print
    """

if __name__ == '__main__':
    def cb_enter(cpv, i, count):
        print '[%s/%s] %s' % (i, count, cpv)

    installed_packages = InstalledPackages(debug=True, cb_enter=cb_enter)
    installed_packages.dump()
