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
import portage
from tools.mirrorparser import MirrorParser
from tools.syncfile import SyncFile

class Mirrors:
    def __init__(self):
        all_urls = self._collect_used_mirror_urls()
        self._mirror_urls = [url for url in
                all_urls if
                url in self._collect_known_mirror_urls()]
        self._total_count = len(all_urls)
        self._secret_count = self._total_count - self.known_count()
        sync_url = self._get_sync_url()
        if sync_url in self._collect_known_sync_urls():
            self._sync_url = sync_url
        else:
            self._sync_url = 'WITHHELD'

    def _collect_used_mirror_urls(self):
        return [e for e in portage.settings['GENTOO_MIRRORS'].split(' ') if e != '']

    def _get_sync_url(self):
        return portage.settings['SYNC']

    def _collect_known_mirror_urls(self):
        sync_file = SyncFile('http://www.gentoo.org/main/en/mirrors.xml?passthru=1', 'mirrors.xml')
        file = open(sync_file.path(), 'r')
        parser = MirrorParser()
        try:
            parser.feed(file.read())
        except EnvironmentError:
            pass
        parser.close()
        file.close()
        return set([url for url, description in parser.lines])

    def _collect_known_sync_urls(self):
        # TODO refactor app-portage/mirrorselect, use list from there
        # and make it a dependency
        sync_dict = [('rsync://rsync.gentoo.org/gentoo-portage', 'Default'),
            ('rsync://rsync.namerica.gentoo.org/gentoo-portage',
                'North America'),
            ('rsync://rsync.samerica.gentoo.org/gentoo-portage',
                'South America'),
            ('rsync://rsync.europe.gentoo.org/gentoo-portage', 'Europe'),
            ('rsync://rsync.asia.gentoo.org/gentoo-portage', 'Asia'),
            ('rsync://rsync.au.gentoo.org/gentoo-portage', 'Australia')]
        return set(k for k, v in sync_dict)

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
        print 'GENTOO_MIRRORS: ' + str(self.get_mirrors())
        print '  Total: ' + str(self.total_count())
        print '  Known: ' + str(self.known_count())
        print '  Secret: ' + str(self.secret_count())

if __name__ == '__main__':
    mirrors = Mirrors()
    mirrors.dump()
