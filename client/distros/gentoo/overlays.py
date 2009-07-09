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

import ConfigParser
import portage
import re
from portage import config
from portage.versions import catpkgsplit
from portage.dbapi.porttree import portdbapi
from tools.maintreedir import main_tree_dir
from tools.syncfile import SyncFile
from tools.overlayparser import OverlayParser

class _Overlays:
    def __init__(self):
        self._fill_overlays()
        tree_config = config()
        tree_config['PORTDIR_OVERLAY'] = ' '.join(self.get_paths())
        tree_config['PORTDIR'] = main_tree_dir()
        self._dbapi = portdbapi(main_tree_dir(), tree_config)

    def _parse_overlay_meta(self, filename):
        parser = OverlayParser()
        file = open(filename, 'r')
        parser.parse(file.read())
        file.close()
        return parser.get()

    def _get_known_overlay_map(self):
        sync_file = SyncFile(
                'http://www.gentoo.org/proj/en/overlays/layman-global.txt',
                'layman-global.txt')
        return self._parse_overlay_meta(sync_file.path())

    def _fill_overlays(self):
        # read layman config
        layman_config = ConfigParser.ConfigParser()
        layman_config.read('/etc/layman/layman.cfg')
        layman_storage_path = layman_config.get('MAIN', 'storage')
        if not layman_storage_path.endswith('/'):
            layman_storage_path = layman_storage_path + '/'
        layman_installed_list_file = layman_config.get('MAIN', 'local_list')
        global_overlay_dict = self._get_known_overlay_map()
        available_installed_overlay_dict = \
                self._parse_overlay_meta(layman_installed_list_file)
        enabled_installed_overlays = \
                portage.settings['PORTDIR_OVERLAY'].split(' ')

        def overlay_name(overlay_location):
            return overlay_location.split('/')[-1]

        url_prefix_pattern = re.compile('^[a-zA-Z+]+://')
        def normalize_repo_url(url):
            res = url
            res = re.sub(url_prefix_pattern, 'xxxxx://', res)
            res = res.replace('://overlays.gentoo.org/svn/',
                    '://overlays.gentoo.org/')
            return res

        def same_repository(a, b):
            return normalize_repo_url(a) == normalize_repo_url(b)

        def is_global(overlay_location):
            name = overlay_name(overlay_location)
            return overlay_location.startswith(layman_storage_path) and \
                    same_repository(
                        available_installed_overlay_dict[name],
                        global_overlay_dict[name])

        global_overlay_paths = [e for e in
                enabled_installed_overlays if is_global(e)]
        global_overlay_names = [overlay_name(e) for e in
                global_overlay_paths]

        self._overlay_paths = global_overlay_paths
        self._overlay_names = global_overlay_names
        self._total_count = len(enabled_installed_overlays)
        self._secret_count = \
                len(enabled_installed_overlays) - len(global_overlay_names)

    def get_names(self):
        return self._overlay_names

    def get_paths(self):
        return self._overlay_paths

    def total_count(self):
        return self._total_count

    def secret_count(self):
        return self._secret_count

    def known_count(self):
        return len(self._overlay_names)

    def is_secret_package(self, cpv):
        try:
            cat, pkg, _, _ = catpkgsplit(cpv)
        except TypeError:
            # version missing
            cat, pkg = cpv.split('/')
            pkg = pkg.split(':')[0]
        cat_pkg = "%s/%s" % (cat, pkg)
        return not self._dbapi.cp_list(cat_pkg)

    def dump(self):
        print 'Names: ' + str(self.get_names())
        print 'Paths: ' + str(self.get_paths())
        print 'Total: ' + str(self.total_count())
        print '  Known: ' + str(self.known_count())
        print '  Secret: ' + str(self.secret_count())


_overlays_instance = None
def Overlays():
    """
    Simple singleton wrapper around _Overlays class
    """
    global _overlays_instance
    if _overlays_instance == None:
        _overlays_instance = _Overlays()
    return _overlays_instance


if __name__ == '__main__':
    overlays = Overlays()
    overlays.dump()
