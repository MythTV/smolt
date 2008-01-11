from sys import argv
from os import chown
from os import chmod
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
                  default='/etc/sysconfig/hw-uuid',
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

if __name__ == "__main__":
    try:
        #this is so horrible, i apologize.
        if opts.force: raise IOError
        uuid = file(opts.uuid_file).read().strip()
    except IOError:
        try:
            uuid=generate_uuid(opts.public)
            file(opts.uuid_file, 'w').write(uuid)
            if opts.secure:
                chown(opts.uuid_file, getpwnam('smolt')[2], -1)
                chmod(opts.uuid_file, stat.S_IRUSR \
                                      ^ stat.S_IWUSR \
                                      ^ stat.S_IRGRP \
                                      ^ stat.S_IWGRP)
        except IOError:
            sys.stderr.write('Unable to determine UUID of system!\n')
            sys.exit(1)
            
def generate_uuid(public=False):
    try:
        uuid = file('/proc/sys/kernel/random/uuid').read().strip()
        if public:
            uuid = "pub_" + uuid
        return uuid
    except IOError:
        raise UUIDError("Cannot generate UUID")
