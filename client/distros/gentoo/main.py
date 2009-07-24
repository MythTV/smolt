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

import os

if __name__ == '__main__':
    import sys
    sys.path.append(os.path.join('..', '..'))
from distros.distro import Distro

class _Gentoo(Distro):
    def name(self):
        return 'gentoo'

    def detected(self, debug=False):
        """
        Returns True if we run on top of Gentoo, else False.
        """
        return os.path.exists('/etc/gentoo-release')

    def gather(self, debug=False):
        def _stage(text):
            print 'Processing %s' % (text)
        # Local imports to not pull missing dependencies in
        # on non-Gentoo machines.
        from globaluseflags import GlobalUseFlags
        from compileflags import CompileFlags
        from mirrors import Mirrors
        from overlays import Overlays
        from packagestar import PackageMask
        from systemprofile import SystemProfile
        from trivials import Trivials
        from installedpackages import InstalledPackages

        _stage('global use flags')
        global_use_flags = GlobalUseFlags()

        _stage('compile flags')
        compile_flags = CompileFlags()

        _stage('mirrors')
        mirrors = Mirrors(debug=debug)

        _stage('overlays')
        overlays = Overlays()

        _stage('package.mask entries')
        user_package_mask = PackageMask()

        _stage('trivials')
        trivials = Trivials()

        _stage('installed packages (takes some time)')
        if debug:
            def cb_enter(cpv, i, count):
                print '[% 3d%%] %s' % (i * 100 / count, cpv)
        else:
            def cb_enter(*_):
                pass
        installed_packages = InstalledPackages(debug=debug, cb_enter=cb_enter)

        machine_data = {}
        machine_data['protocol'] = '1.0'
        machine_data['global_use_flags'] = global_use_flags.serialize()
        machine_data['compile_flags'] = compile_flags.serialize()
        machine_data['mirrors'] = mirrors.serialize()
        machine_data['overlays'] = overlays.serialize()
        machine_data['user_package_mask'] = user_package_mask.serialize()
        machine_data['system_profile'] = system_profile.serialize()
        for container in (trivials, ):
            for k, v in container.serialize().items():
                key = k.lower()
                if key in machine_data:
                    raise Exception('Unintended key collision')
                machine_data[key] = v
        machine_data['installed_packages'] = installed_packages.serialize()
        return machine_data


_gentoo_instance = None
def Gentoo():
    """
    Simple singleton wrapper around _Gentoo class
    """
    global _gentoo_instance
    if _gentoo_instance == None:
        _gentoo_instance = _Gentoo()
    return _gentoo_instance


if __name__ == '__main__':
    # Enable auto-flushing for stdout
    import sys
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

    from simplejson import JSONEncoder
    print JSONEncoder(indent=2, sort_keys=True).encode(
        Gentoo().gather(debug=True))
