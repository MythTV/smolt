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
from globaluseflags import GlobalUseFlags
from worldset import WorldSet
from packagestar import PackageMask, PackageUnmask, ProfilePackageMask

class InstalledPackages:
    def __init__(self, debug=False):
        self._cpv_flag_list = []
        var_tree = vartree()
        installed_cpvs = var_tree.getallcpv()
        self._total_count = 0
        self._private_count = 0
        for cpv in installed_cpvs:
            self._total_count = self._total_count + 1
            added = self._process(var_tree, cpv, debug=debug)
            if not added:
                self._private_count = self._private_count + 1

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

        private_package = Overlays().is_private_package(cpv)
        if debug and private_package:
            print '  cpv "%s" belongs to a private package' % (cpv)

        from_private_overlay = repository and \
            Overlays().is_private_overlay_name(repository)
        if from_private_overlay:
            if debug:
                print '  repository "%s" is private for cpv "%s", stripping' % \
                    (repository, cpv)
            repository = ''

        """
        Notes on the line of code after:

        -   We collect private packages iff they come from a non-private
            overlay, because that means they were in the before and are
            actually not private.  An example would be media-sounds/xmms

        -   We collect packages from private overlays iff the package also
            exists in a non-private overlay.  An example would be that
            you posted your ebuild to bugs.gentoo.org and somebody added
            it to the tree in the meantime.

        Conclusion:  'and' is wanted below, not 'or'
        """
        if private_package and from_private_overlay:
            if debug:
                print '  --> skipping cpv "%s"' % (cpv)
            return False

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
        flags = set(e for e in USE.split() if use_flags.is_known(e)) & \
            set(x.lstrip("+-") for x in IUSE.split() if use_flags.is_known(x))
        entry = [package_name, version_revision, SLOT, keyword_status,
            masked, unmasked, is_in_world, repository, sorted(flags)]
        self._cpv_flag_list.append(entry)
        return True

    def total_count(self):
        return self._total_count

    def private_count(self):
        return self._private_count

    def known_count(self):
        return len(self._cpv_flag_list)

    def dump(self):
        print 'Packages:'
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

if __name__ == '__main__':
    installed_packages = InstalledPackages(debug=True)
    installed_packages.dump()
