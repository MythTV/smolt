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
from portage.const import REPO_NAME_LOC
import re
import os
from portage import config
from portage.versions import catpkgsplit
from portage.dbapi.porttree import portdbapi
from tools.maintreedir import main_tree_dir
from tools.syncfile import SyncFile
from tools.overlayparser import OverlayParser


_MAIN_TREE_WHITELIST = (
    "gentoo",
    "funtoo",
    "gentoo_prefix",
)

_REPO_NAME_MISMATCH_WHITELIST = (
    "bangert-ebuilds",  # bangert
    "china",  # gentoo-china
    "dev-jokey",  # jokey
    "digital-trauma.de",  # trauma
    "Falco's git overlay",  # falco
    "gcj-overlay",  # java-gcj-overlay
    "geki-overlay",  # openoffice-geki
    "gentoo-haskell",  # haskell
    "gentoo-lisp-overlay",  # lisp
    "kde4-experimental",  # kde
    "kde",  # kde-testing
    "leio-personal",  # leio
    "maekke's overlay",  # maekke
    "majeru",  # oss-overlay
    "mpd-portage",  # mpd
    "ogo-lu_zero",  # lu_zero
    "pcsx2-overlay",  # pcsx2
    "proaudio",  # pro-audio
    "scarabeus_local_overlay",  # scarabeus
    "soor",  # soor-overlay
    "steev_github",  # steev
    "suka's dev overlay - experimental stuff of all sorts",  # suka
    "tante_overlay",  # tante
    "vdr-xine-overlay",  # vdr-xine
    "webapp-experimental",  # webapps-experimental
)


class _Overlays:
    def __init__(self):
        self._fill_overlays()
        tree_config = config()
        tree_config['PORTDIR_OVERLAY'] = ' '.join(self.get_active_paths())
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
        self._global_overlays_dict = self._get_known_overlay_map()
        enabled_installed_overlays = \
                portage.settings['PORTDIR_OVERLAY'].split(' ')

        def overlay_name(overlay_location):
            repo_name_file = os.path.join(overlay_location, REPO_NAME_LOC)
            file = open(repo_name_file, 'r')
            name = file.readline().strip()
            file.close()
            return name

        def is_non_private(overlay_location):
            try:
                name = overlay_name(overlay_location)
            except:
                return False
            return (name in self._global_overlays_dict)

        non_private_active_overlay_paths = [e for e in
                enabled_installed_overlays if is_non_private(e)]
        non_private_active_overlay_names = [overlay_name(e) for e in
                non_private_active_overlay_paths]

        self._active_overlay_paths = non_private_active_overlay_paths
        self._active_overlay_names = non_private_active_overlay_names
        self._total_count = len(enabled_installed_overlays)
        self._private_count = \
                len(enabled_installed_overlays) - len(non_private_active_overlay_names)

    def get_active_names(self):
        return self._active_overlay_names

    def get_active_paths(self):
        return self._active_overlay_paths

    def total_count(self):
        return self._total_count

    def private_count(self):
        return self._private_count

    def known_count(self):
        return len(self._active_overlay_names)

    def is_private_package(self, atom):
        cp = portage.dep_getkey(atom)
        return not self._dbapi.cp_list(cp)

    def is_private_overlay_name(self, overlay_name):
        if overlay_name in _MAIN_TREE_WHITELIST:
            return False

        if overlay_name in _REPO_NAME_MISMATCH_WHITELIST:
            return False

        return not overlay_name in self._global_overlays_dict

    def dump(self):
        print 'Active overlays:'
        print '  Names:'
        print self.get_active_names()
        print '  Paths:'
        print self.get_active_paths()
        print '  Total: ' + str(self.total_count())
        print '    Known: ' + str(self.known_count())
        print '    Private: ' + str(self.private_count())
        print


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
