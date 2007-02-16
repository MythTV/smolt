#!/usr/bin/python

import sys
import getopt
import urlgrabber.grabber
import smolt

DEBUG = 0
printOnly = 0
smoonURL = 'http://smolt.fedoraproject.org/'
user_agent = 'smolt/0.8'

sys.path.append('/usr/share/smolt/client')

def error(message):
    print >> sys.stderr, message

def ignoreDevice(device):
    ignore = 1
    if device.bus == 'Unknown':
        return 1
    if device.bus == 'usb' and device.type == None:
        return 1
    if device.bus == 'usb' and device.driver == 'hub':
        return 1
    if device.bus == 'sound' and device.driver == 'Unknown':
        return 1
    if device.bus == 'pnp' and (device.driver == 'Unknown' or device.driver == 'system'):
        return 1
    return 0

def debug(message):
    if DEBUG == 1:
        print message

def help():
    print "Usage:"
    print "     -h,--help           Display this help menu"
    print "     -d,--debug          Enable debug information"
    print "     -p,--printOnly      Print Information only, do not send"
    print "     -s,--server=        serverUrl (http://yourSmoonServer/"
    print "     -u,--useragent=     User Agent"
    sys.exit(2)

try:
    opts, args = getopt.getopt(sys.argv[1:], 'phds:u:', ['help', 'debug', 'printOnly', 'server=', 'useragent=', 'user_agent='])
except getopt.GetoptError:
    help()
    sys.exit(2)

for opt, arg in opts:
    if opt in ('-h', '--help'):
        help()
    if opt in ('-d', '--debug'):
        DEBUG = 1
    if opt in ('-s', '--server'):
        smoonURL = arg
    if opt in('-p', '--printOnly'):
        printOnly = 1
    if opt in ('-u', '--useragent', '--user_agent'):
        user_agent = arg
        
# read the profile
profile = smolt.Hardware()

print 'We are about to send the following information to the Fedora Smolt server:'
print
print '\tUUID: %s' % profile.host.UUID
print '\tOS: %s' % profile.host.os
print '\tdefaultRunlevel: %s' % profile.host.defaultRunlevel
print '\tlanguage: %s' % profile.host.language
print '\tplatform: %s' % profile.host.platform
print '\tbogomips: %s' % profile.host.bogomips
print '\tCPUVendor: %s' % profile.host.cpuVendor
print '\tnumCPUs: %s' % profile.host.numCpus
print '\tCPUSpeed: %s' % profile.host.cpuSpeed
print '\tsystemMemory: %s' % profile.host.systemMemory
print '\tsystemSwap: %s' % profile.host.systemSwap
print '\tvendor: %s' % profile.host.systemVendor
print '\tsystem: %s' % profile.host.systemModel
print
print '\t\t Devices'
print '\t\t================================='
''' Returns 1 for ignored devices and 0 otherwise '''


for device in profile.devices:
    try:
        Bus = profile.devices[device].bus
        VendorID = profile.devices[device].vendorid
        DeviceID = profile.devices[device].deviceid
        Driver = profile.devices[device].driver
        Type = profile.devices[device].type
        Description = profile.devices[device].description
    except:
        continue
    else:
        if not ignoreDevice(profile.devices[device]):
            print '\t\t(%s:%s) %s, %s, %s, %s' % (VendorID, DeviceID, Bus, Driver, Type, Description)

if printOnly:
    sys.exit(0)

print 'Transmitting ...'

grabber = urlgrabber.grabber.URLGrabber(user_agent=user_agent)

sendHostStr = profile.hostSendString

debug('smoon server URL: %s' % smoonURL)
debug('sendHostStr: %s' % profile.hostSendString)
debug('Sending Host')

try:
    o=grabber.urlopen('%s/add' % smoonURL, data=sendHostStr, http_headers=(
                    ('Content-length', '%i' % len(sendHostStr)),
                    ('Content-type', 'application/x-www-form-urlencoded')))
except urlgrabber.grabber.URLGrabError, e:
    error('Error contacting Server: %s' % e)
    sys.exit(1)
else:
    o.close()

for device in profile.devices:
    if not ignoreDevice(profile.devices[device]):
        sendDeviceStr = profile.devices[device].deviceSendString
        debug('Sending device')
        debug('sendDeviceStr: %s' % sendDeviceStr)
        try:
            o=grabber.urlopen('%s/addDevice' % smoonURL, data=sendDeviceStr, http_headers=(('Content-length', '%i' % len(sendDeviceStr)),
                                                                                       ('Content-type', 'application/x-www-form-urlencoded')))
        except urlgrabber.grabber.URLGrabError, e:
            error('Error contacting server: %s' % e)
            sys.exit(1)
        else:
            o.close()

print 'Thank you, your uuid (in /etc/sysconfig/hw-uuid), is %s' % profile.host.UUID
