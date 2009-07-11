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

import sets
import urlparse
import portage
from mirrorselect.mirrorparser3 import MirrorParser3, MIRRORS_3_XML
from tools.syncfile import SyncFile

class Mirrors:
    def __init__(self):
        all_urls = self._collect_used_mirror_urls()
        self._mirror_urls = [url for url in
                all_urls if
                url in self._collect_known_mirror_urls()]
        self._total_count = len(all_urls)
        self._secret_count = self._total_count - self.known_count()
        self._sync_url = self._get_sync_url()

    def _collect_used_mirror_urls(self):
        return [e for e in
            portage.settings['GENTOO_MIRRORS'].split(' ') if e != '']

    def _get_sync_url(self):
        sync_url = portage.settings['SYNC']
        if (sync_url == None) or (sync_url.isspace()):
            sync_url = '<using non-rsync tree>'
        else:
            parsed = urlparse.urlparse(sync_url)
            if (parsed.hostname == None) or not (\
                    parsed.hostname.endswith('gentoo.org') or \
                    parsed.hostname.endswith('prefix.freens.org')):
                sync_url = 'WITHHELD'
        return sync_url

    def _collect_known_mirror_urls(self):
        sync_file = SyncFile(
            MIRRORS_3_XML,
            'mirrors3.xml')
        file = open(sync_file.path(), 'r')
        parser = MirrorParser3()
        try:
            parser.parse(file.read())
        except EnvironmentError:
            pass
        file.close()
        return set(parser.uris())

    def get_mirrors(self):
        return self._mirror_urls

    def get_sync(self):
        return self._sync_url

    def total_count(self):
        return self._total_count

    def secret_count(self):
        return self._secret_count

    def known_count(self):
        return len(self._mirror_urls)

    def dump(self):
        print 'SYNC: ' + str(self.get_sync())
        print 'GENTOO_MIRRORS:'
        print self.get_mirrors()
        print '  Total: ' + str(self.total_count())
        print '    Known: ' + str(self.known_count())
        print '    Secret: ' + str(self.secret_count())
        print

if __name__ == '__main__':
    mirrors = Mirrors()
    mirrors.dump()
