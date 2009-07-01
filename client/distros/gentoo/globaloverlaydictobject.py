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

import urllib
import os
from xml.etree import ElementTree as ET

# TODO
SMOLT_CONFIG_DIR = os.path.expanduser('~/.smolt')
REMOTE_LOCATION = 'http://www.gentoo.org/proj/en/overlays/layman-global.txt'
LOCAL_LOCATION = SMOLT_CONFIG_DIR + '/layman-global.txt'
DIR_EXISTS_ERRNO = 17


def read_overlay_xml(filename):
    overlay_url_to_name_map = {}
    file = open(filename, 'r')
    for i in ET.XML(file.read()):
        try:
            overlay_url = i.attrib['src']
            overlay_name = i.attrib['name']
            overlay_url_to_name_map[overlay_name] = overlay_url
        except KeyError:
            pass
    file.close()
    return overlay_url_to_name_map


class GlobalOverlayDict:
    def __init__(self):
        try:
            os.mkdir(SMOLT_CONFIG_DIR, 0700)
        except OSError, e:
            if e.errno != DIR_EXISTS_ERRNO:
                raise e
        self._reset()

    def create(self):
        # TODO return write-protected copy?
        return self.overlay_url_to_name_map

    def _reset(self):
        self.overlay_url_to_name_map = {}
        if self._sync_needed():
            self._sync()
        self._read()

    def _sync_needed(self):
        # TODO
        return True

    def _sync(self):
        remote_file = urllib.urlopen(REMOTE_LOCATION)
        local_file = open(LOCAL_LOCATION, 'w')
        local_file.write(remote_file.read())
        remote_file.close()
        local_file.close()

    def _read(self):
        self.overlay_url_to_name_map = read_overlay_xml(LOCAL_LOCATION)

if __name__ == '__main__':
    for k, v in GlobalOverlayDict().create().items():
        print "%s = %s" % (k, v)
