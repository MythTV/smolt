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

import sys
import os
from gentoo.compileflags import CompileFlags
from gentoo.globaluseflags import GlobalUseFlags
from gentoo.installedpackages import InstalledPackages
from gentoo.makeopts import MakeOpts
from gentoo.mirrors import Mirrors
from gentoo.overlays import Overlays
from gentoo.packagestar import PackageMask
from gentoo.systemprofile import SystemProfile
from gentoo.trivialscalars import TrivialScalars
from gentoo.trivialvectors import TrivialVectors

def stage(text):
    print 'Processing %s' % (text)

if __name__ == '__main__':
    # Enable auto-flushing for stdout
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

    stage('global use flags')
    global_use_flags = GlobalUseFlags()

    stage('compile flags')
    compile_flags = CompileFlags()

    stage('make opts')
    make_opts = MakeOpts()

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
    installed_packages = InstalledPackages(debug=True)

    print
    for i in (installed_packages, global_use_flags, compile_flags,
            make_opts, mirrors, overlays, user_package_mask, system_profile,
            trivial_scalars, trivial_vectors):
        i.dump()
