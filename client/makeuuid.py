from sys import argv
from os import chown
from os import chmod
import stat
from pwd import getpwnam

if __name__ == "__main__":
    hw_uuid_file = argv[1]
    secure = argv[2]
    if secure == "True":
        secure = True
        print "do secure"
    else:
        secure = False
    try:
        uuid = file(hw_uuid_file).read().strip()
    except IOError:
        try:
            uuid = file('/proc/sys/kernel/random/uuid').read().strip()
            file(hw_uuid_file, 'w').write(uuid)
            print "secure = %s" % secure
            if secure:
                print "doing secure"
                chown(hw_uuid_file, getpwnam('smolt')[2], -1)
                chmod(hw_uuid_file, stat.S_IRUSR \
                                      ^ stat.S_IWUSR \
                                      ^ stat.S_IRGRP \
                                      ^ stat.S_IWGRP)
        except IOError:
            sys.stderr.write('Unable to determine UUID of system!\n')
            sys.exit(1)
