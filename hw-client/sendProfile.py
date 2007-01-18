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
            sys.stderr.write('Unable to save UUID, continuing...\n')
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

sendHostStr = "UUID=%s&lsbRelease=%s&OS=%s&defaultRunlevel=%s&language=%s&platform=%s&bogomips=%s&CPUVendor=%s&numCPUs=%s&CPUSpeed=%s&systemMemory=%s&systemSwap=%s&vendor=%s&system=%s" % (UUID, lsbRelease, OS, defaultRunlevel, language, platform, bogomips, CPUVendor, numCPUs, CPUSpeed, systemMemory, systemSwap, vendor, system)


print 'We are about to send the following information to the Fedora Smolt server:'
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

print 'Transmitting ...'

grabber = urlgrabber.grabber.URLGrabber()

#commands.getstatusoutput('/usr/bin/wget -O /dev/null -q http://publictest4.fedora.redhat.com/add --post-data="%s"' % sendHostStr)[1]

o=grabber.urlopen('http://publictest4.fedora.redhat.com/add', data=sendHostStr, http_headers=(('Content-length', '%i' % len(sendHostStr)),
                                                                                            ('Content-type', 'application/x-www-form-urlencoded')))
print `o.read()`
o.close()

print 'sent host data'

for device in hw:
    try:
        Bus = device['bus']
        Driver = device['driver']
        Class = device['class']
        Description = device['desc']
    except:
        continue
    else:
        sendDeviceStr = "UUID=%s&Bus=%s&Driver=%s&Class=%s&Description=%s" % (UUID, Bus, Driver, Class, Description)
        #commands.getstatusoutput('/usr/bin/wget -O /dev/null -q http://publictest4.fedora.redhat.com/addDevice --post-data="%s"' % sendDeviceStr)[1]
        o=grabber.urlopen('http://publictest4.fedora.redhat.com/addDevice', data=sendDeviceStr, http_headers=(('Content-length', '%i' % len(sendDeviceStr)),
                                                                                                              ('Content-type', 'application/x-www-form-urlencoded')))
        print `o.read()`
        o.close()
        
        print 'sent device data'

print 'Thankyou, your uuid (in /etc/sysconfig/hw-uuid), is %s' % UUID
