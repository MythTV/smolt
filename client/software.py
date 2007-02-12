import os
import commands
import re

def read_lsb_release():
    if os.access('/usr/bin/lsb_release', os.X_OK):
        return commands.getstatusoutput('/usr/bin/lsb_release')[1].strip()
    return ''

initdefault_re = re.compile(r':(\d+):initdefault:')

def read_runlevel():
    defaultRunlevel = 'Unknown'
    try:
        inittab = file('/etc/inittab').read()
        match = initdefault_re.search(inittab)
        if match:
            defaultRunlevel = match.group(1)
    except IOError:
        sys.stderr.write('Unable to read /etc/inittab.')
    return defaultRunlevel.strip()

def read_os():
    try:
        return file('/etc/redhat-release').read().strip()
    except IOError:
        return 'Unknown'
