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

from simplejson import JSONEncoder

import sys
import os
from globaluseflags import GlobalUseFlags
from compileflags import CompileFlags
from mirrors import Mirrors
from overlays import Overlays
from packagestar import PackageMask
from systemprofile import SystemProfile
from trivialscalars import TrivialScalars
from trivialvectors import TrivialVectors
from installedpackages import InstalledPackages

def stage(text):
    print 'Processing %s' % (text)

def main():
    # Enable auto-flushing for stdout
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

    stage('global use flags')
    global_use_flags = GlobalUseFlags()

    stage('compile flags')
    compile_flags = CompileFlags()

    stage('mirrors')
    mirrors = Mirrors()

    stage('overlays')
    overlays = Overlays()

    stage('package.mask entries')
    user_package_mask = PackageMask()

    stage('system profile')
    system_profile = SystemProfile()

    stage('trivial scalars')
    trivial_scalars = TrivialScalars()

    stage('trivial vectors')
    trivial_vectors = TrivialVectors()

    stage('installed packages (takes some time)')
    def cb_enter(cpv, i, count):
        print '[% 3d%%] %s' % (i * 100 / count, cpv)
    installed_packages = InstalledPackages(debug=True, cb_enter=cb_enter)

    # Body
    gentoo_body = {}
    gentoo_body['global_use_flags'] = global_use_flags.serialize()
    gentoo_body['compile_flags'] = compile_flags.serialize()
    gentoo_body['mirrors'] = mirrors.serialize()
    gentoo_body['overlays'] = overlays.serialize()
    gentoo_body['user_package_mask'] = user_package_mask.serialize()
    gentoo_body['system_profile'] = system_profile.serialize()
    for container in (trivial_scalars, trivial_vectors):
        for k, v in container.serialize().items():
            key = k.lower()
            if key in gentoo_body:
                raise Exception('Unintended key collision')
            gentoo_body[key] = v
    gentoo_body['installed_packages'] = installed_packages.serialize()

    # Head
    gentoo_head = {
        'distro':'gentoo',
        'protocol':'1.0',
    }

    gentoo = [gentoo_head, gentoo_body]
    print JSONEncoder(indent=2, sort_keys=True).encode(gentoo)

if __name__ == '__main__':
    main()
