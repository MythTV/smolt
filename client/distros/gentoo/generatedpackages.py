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

_COLLECT_CROSSDEV = True  # TODO configurable
_COLLECT_GCPAN = True  # TODO configurable

class _GeneratedPackages:
    def __init__(self):
        pass

    def is_generated_cat(self, cat):
        return self._is_crossdev_cat(cat) or self._is_gcpan_cat(cat)

    def is_private_cat(self, cat):
        return (self._is_crossdev_cat(cat) and not _COLLECT_CROSSDEV) or \
            (self._is_gcpan_cat(cat) and not _COLLECT_GCPAN)

    def _is_crossdev_cat(self, cat):
        return cat.startswith('cross-')

    def _is_gcpan_cat(self, cat):
        return cat == 'perl-gcpan'


_generated_packages = None
def GeneratedPackages():
    """
    Simple singleton wrapper around _GeneratedPackages class
    """
    global _generated_packages
    if _generated_packages == None:
        _generated_packages = _GeneratedPackages()
    return _generated_packages


if __name__ == '__main__':
    generated_packages = GeneratedPackages()
    for cpv in ('perl-gcpan/Set-Object-1.27',
            'cross-spu-elf/newlib-1.16.0',
            'dev-util/git',
            ):
        cat = cpv.split('/')[0]
        print '%s: generated=[%s] private=[%s]' % \
            (cpv, str(generated_packages.is_generated_cat(cat)),
            str(generated_packages.is_private_cat(cat)))
