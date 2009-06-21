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

try:
    import portage
except ImportError:
    import sys
    sys.stderr.write("Could not 'import portage'\n")
    sys.exit(1)

import re
import sets
import os

class GentooSystemConfig:
    def __init__(self):
        self.portage = {}
        self.infered = {}

        # List of all vars:
        #   grep -h '^\(# *\)\?[^ ]\+=' /etc/make.{conf,globals} \
        #       $(find /usr/portage/profiles/ -name make.defaults) \
        #     | sed -e 's|^# *||' -e 's|=.*$||' | sort -u

        # vectors
        for var in ('ACCEPT_KEYWORDS', 'VIDEO_CARDS', 'ALSA_CARDS',
                'GENTOO_MIRRORS', 'FEATURES', 'LINGUAS'):
            self._fill_vector(var)
        for var in ('CFLAGS', 'CXXFLAGS', 'LDFLAGS'):
            self._fill_gcc_flags(var)
        self._fill_make_flags()
        self._fill_use_flags()
        self._fill_overlays()

        # scalars
        for var in ('ARCH', 'CHOST', 'USERLAND', 'KERNEL', 'SYNC', 'USE_ORDER',
                'PORTAGE_NICENESS', 'PORTAGE_FETCH_CHECKSUM_TRY_MIRRORS',
                'PORTAGE_ECLASS_WARNING_ENABLE', 'PORTAGE_BINHOST'):
            self._fill_scalar(var)

        # infer stuff
        self.infered['NUMBER_OF_MIRRORS'] = len(self.portage['GENTOO_MIRRORS'])
        self.infered['NUMBER_OF_OVERLAYS'] = len(self.infered['OVERLAYS'])
        self.infered['SYSTEM_PROFILE'] = os.path.realpath(
                portage.settings.profile_path).replace(
                '/usr/portage/profiles/', '')

    def _dump(self):
        print "Copied from portage (with filtering)"
        for k, v in gentoo.portage.items():
            print "  %s = %s" % (k, v)
        print
        print "Infered or transformed"
        for k, v in gentoo.infered.items():
            print "  %s = %s" % (k, v)

    def _privacy_filter_make_flags(self, make_flags):
        # TODO any?
        return make_flags

    def _privacy_filter_gcc_flags(self, gcc_flags):
        # TODO more?
        private_flag_prefixes = ('-I', '-L', '-l', '--library=',
                '--library-path=')
        def is_private(gcc_flag):
            for prefix in private_flag_prefixes:
                if gcc_flag.startswith(prefix):
                    return True
            return False
        return [e for e in gcc_flags if not is_private(e)]

    def _fill_gcc_flags(self, key):
        self.portage[key] = self._privacy_filter_gcc_flags(
                portage.settings[key].split(' '))

    def _fill_make_flags(self):
        key = 'MAKEOPTS'
        self.portage[key] = self._privacy_filter_make_flags(
                portage.settings[key].split(' '))

    def _fill_scalar(self, key):
        self.portage[key] = portage.settings[key]

    def _fill_vector(self, key):
        self.portage[key] = [e for e in portage.settings[key].split(' ') if e != '']

    def _registered_global_use_flags(self):
        try:
            f = open('/usr/portage/profiles/use.desc', 'r')
            lines = [re.sub('^([^ ]+) - .*\\n', '\\1', l) for l in
                    f.readlines() if re.match('^[^ ]+ - ', l)]
            f.close()
            return set(lines)
        except IOError:
            return set()

    def _registered_local_use_flags(self):
        try:
            f = open('/usr/portage/profiles/use.local.desc', 'r')
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
        self.infered['NUMBER_OF_ALL_GLOBAL_USE_FLAGS'] = \
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
        non_private_global_use_flags = [e for e in non_expand_use_flags
                if is_non_private(e)]
        self.portage['USE'] = non_private_global_use_flags
        self.infered['NUMBER_OF_PRIVATE_GLOBAL_USE_FLAGS'] = \
                len(non_expand_use_flags) - len(non_private_global_use_flags)

        # Partition into global and local, prefer global in doubt
        # Check against global global set is faster as it's much smaller
        global_global_count = 0
        local_global_count = 0
        for use_flag in non_private_global_use_flags:
            if use_flag in registered_global_use_flags:
                global_global_count = global_global_count + 1
            else:
                local_global_count = local_global_count + 1
        self.infered['NUMBER_OF_GLOBAL_GLOBAL_USE_FLAGS'] = global_global_count
        self.infered['NUMBER_OF_LOCAL_GLOBAL_USE_FLAGS'] = local_global_count

    def _fill_overlays(self):
        def is_private(overlay_location):
            # TODO use %{storage} from /etc/layman/layman.cfg?
            return not overlay_location.startswith('/usr/local/portage/layman/')
        def overlay_name(overlay_location):
            # TODO look up from file instead?
            return overlay_location.replace('/usr/local/portage/layman/', '')
        self.infered['OVERLAYS'] = [overlay_name(e) for e in
                portage.settings['PORTDIR_OVERLAY'].split(' ')
                if not is_private(e)]

if __name__ == '__main__':
    gentoo = GentooSystemConfig()
    gentoo._dump()
