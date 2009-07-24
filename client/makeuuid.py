# smolt - Fedora hardware profiler
#
# Copyright (C) 2007 Yaakov M. Nemoy <loupgaroublond@gmail.com>
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
import stat
from pwd import getpwnam
from optparse import OptionParser
from i18n import _

class UUIDError(Exception):
    pass

parser = OptionParser(version = "1.monkey.0")

parser.add_option('-d', '--debug',
                  dest = 'DEBUG',
                  default = False,
                  action = 'store_true',
                  help = _('enable debug information'))
parser.add_option('-f', '--force',
                  dest='force',
                  default=False,
                  action='store_true',
                  help=_('force makeuuid to generate a new UUID even when one exists'))
parser.add_option('-o', '--output',
                  dest='uuid_file',
                  default='/etc/smolt/hw-uuid',
                  help=_('the uuid file'))
parser.add_option('-s', '--secure',
                  dest='secure',
                  action='store_true',
                  default=False,
                  help=_('generate a secure key'))
parser.add_option('-p', '--public',
                  dest='public',
                  action='store_true',
                  default=False,
                  help=_('generate a public key'))

(opts, args) = parser.parse_args()

def generate_uuid(public=False):
    try:
        uuid = file('/proc/sys/kernel/random/uuid').read().strip()
        if public:
            uuid = "pub_" + uuid
        return uuid
    except IOError:
        raise UUIDError("Could not generate UUID.")

if __name__ == "__main__":
    try:
        #this is so horrible, i apologize.
        if opts.force: raise IOError
        uuid = file(opts.uuid_file).read().strip()
    except IOError:
        try:
            uuid_dir = os.path.dirname(opts.uuid_file)
            if not os.path.exists(uuid_dir):
                os.makedirs(uuid_dir, 0755)
            uuid=generate_uuid(opts.public)
            file(opts.uuid_file, 'w').write(uuid)
            if opts.secure:
                os.chown(opts.uuid_file, getpwnam('smolt')[2], -1)
                os.chmod(opts.uuid_file, stat.S_IRUSR \
                                      ^ stat.S_IWUSR \
                                      ^ stat.S_IRGRP \
                                      ^ stat.S_IWGRP)
        except IOError:
            sys.stderr.write('Could not store UUID.\n')
            sys.exit(1)

