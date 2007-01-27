#!/usr/bin/python

import hardware
import sys
import os
import commands
import re
import urlgrabber.grabber

try:
    UUID = file('/etc/sysconfig/hw-uuid').read()
except IOError:
    try:
        UUID = file('/proc/sys/kernel/random/uuid').read()
        try:
            file('/etc/sysconfig/hw-uuid', 'w').write(UUID)
        except:
            print 'couldn\'t write'
    except IOError:
        sys.stderr.write('Unable to determine UUID of system!\n')
        sys.exit(1)

hw = hardware.Hardware()
lsbRelease = commands.getstatusoutput('/usr/bin/lsb_release')[1]

try:
    OS = file('/etc/redhat-release').read()
except IOError:
    OS = 'Unknown'

initdefault_re = re.compile(r':(\d+):initdefault:')
defaultRunlevel = 'Unknown'
try:
    inittab = file('/etc/inittab').read()
    match = initdefault_re.search(inittab)
    if match:
        defaultRunlevel = match.group(1)
except IOError:
    sys.stderr.write('Unable to read /etc/inittab, continuing...')
    
language = os.environ['LANG']

platform = bogomips = CPUVendor = numCPUs = CPUSpeed = systemMemory = systemSwap = vendor = system = ''

for device in hw:
    try:
        platform = device['platform']
        bogomips = device['bogomips']
        CPUVendor = "%s - %s" % (device['type'], device['model'])
        numCPUs = device['count']
        CPUSpeed = device['speed']
    except:
        pass
    try:
        systemMemory = device['ram']
        systemSwap = device['swap']
    except:
        pass
    try:
        vendor = device['vendor']
        system = device['system']
    except:
        pass



print 'We would send the following information to the Fedora Smolt server:'
print
print '\tUUID: %s' % UUID
print '\tlsbRelease: %s' % lsbRelease
print '\tOS: %s' % OS
print '\tdefaultRunlevel: %s' % defaultRunlevel
print '\tlanguage: %s' % language
print '\tplatform: %s' % platform
print '\tbogomips: %s' % bogomips
print '\tCPUVendor: %s' % CPUVendor
print '\tnumCPUs: %s' % numCPUs
print '\tCPUSpeed: %s' % CPUSpeed
print '\tsystemMemory: %s' % systemMemory
print '\tsystemSwap: %s' % systemSwap
print '\tvendor: %s' % vendor
print '\tsystem: %s' % system
print
print '\t\t Devices'
print '\t\t================================='
for device in hw:
    try:
        Bus = device['bus']
        Driver = device['driver']
        Class = device['class']
        Description = device['desc']
    except:
        continue
    else:
        print '\t\t%s, %s, %s, %s' % (Bus, Driver, Class, Description)

