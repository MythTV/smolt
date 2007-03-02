#!/usr/bin/python

import sys
import getopt
import urlgrabber.grabber
import smolt
import time
from urllib import urlencode
from urlparse import urljoin

DEBUG = 0
printOnly = 0
autoSend = 0
smoonURL = 'http://smolt.fedoraproject.org/'
smoltProtocol = '.91'
user_agent = 'smolt/%s' % smoltProtocol
retry = 0

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
    print "     -a,--autoSend       Don't prompt to send, just send"
    print "     -s,--server=        serverUrl (http://yourSmoonServer/)"
    print "     -r,--retry          Continue to send until success"
    print "     -u,--useragent=     Specify HTTP user agent (default '%s')" % user_agent
    sys.exit(2)

def serverMessage(page):
    for line in page.split("\n"):
        if 'ServerMessage:' in line:
            print 'Server Message: "%s"' % line.split('ServerMessage: ')[1]
            if 'Critical' in line:
                sys.exit(3)

try:
    opts, args = getopt.getopt(sys.argv[1:], 'phadrs:u:', ['help', 'debug', 'printOnly', 'autoSend', 'server=', 'retry', 'useragent=', 'user_agent='])
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
    if opt in('-r', '--retry'):
        retry = 1
    if opt in('-a', '--autoSend'):
        autoSend = 1
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
print '\tCPUModel: %s' % profile.host.cpuModel
print '\tnumCPUs: %s' % profile.host.numCpus
print '\tCPUSpeed: %s' % profile.host.cpuSpeed
print '\tsystemMemory: %s' % profile.host.systemMemory
print '\tsystemSwap: %s' % profile.host.systemSwap
print '\tvendor: %s' % profile.host.systemVendor
print '\tsystem: %s' % profile.host.systemModel
print '\tformfactor: %s' % profile.host.formfactor
print '\tkernel: %s' % profile.host.kernelVersion
print
print '\t\t Devices'
print '\t\t================================='

devices = []

for device in profile.devices:
    try:
        Bus = profile.devices[device].bus
        VendorID = profile.devices[device].vendorid
        DeviceID = profile.devices[device].deviceid
        SubsysVendorID = profile.devices[device].subsysvendorid
        SubsysDeviceID = profile.devices[device].subsysdeviceid
        Driver = profile.devices[device].driver
        Type = profile.devices[device].type
        Description = profile.devices[device].description
    except:
        continue
    else:
        if not ignoreDevice(profile.devices[device]):
            print '\t\t(%s:%s:%s:%s) %s, %s, %s, %s' % (VendorID, DeviceID, SubsysVendorID, SubsysDeviceID, Bus, Driver, Type, Description)
            devices.append('%s|%s|%s|%s|%s|%s|%s|%s' % (VendorID, DeviceID, SubsysVendorID, SubsysDeviceID, Bus, Driver, Type, Description))

if not autoSend:
    if printOnly:
        sys.exit(0)
    else:
        send = raw_input("\nSend this information to the Smolt server? (y/n) ")
        if send.lower() != 'y':
            error('Exiting...')
            sys.exit(4)


print 'Transmitting ...'


def send():
    grabber = urlgrabber.grabber.URLGrabber(user_agent=user_agent)
    
    sendHostStr = profile.hostSendString
    
    debug('smoon server URL: %s' % smoonURL)
    try:
        token = grabber.urlopen('%s/token?UUID=%s' % (smoonURL, profile.host.UUID))
    except urlgrabber.grabber.URLGrabError, e:
        error('Error contacting Server: %s' % e)
        return 1
    else:
        for line in token.read().split('\n'):
            if 'tok' in line:
                tok = line.split(': ')[1]
        token.close()
    
    try:
        tok = tok
    except NameError, e:
        error('Communication with server failed')
        return 1
    
    sendHostStr = sendHostStr + '&token=%s&smoltProtocol=%s' % (tok, smoltProtocol)
    debug('sendHostStr: %s' % profile.hostSendString)
    debug('Sending Host')
    
    try:
        o=grabber.urlopen('%s/add' % smoonURL, data=sendHostStr, http_headers=(
                        ('Content-length', '%i' % len(sendHostStr)),
                        ('Content-type', 'application/x-www-form-urlencoded')))
    except urlgrabber.grabber.URLGrabError, e:
        error('Error contacting Server: %s' % e)
        return 1
    else:
        serverMessage(o.read())
        o.close()
    
    deviceStr = ''
    for dev in devices:
        deviceStr = deviceStr + dev + '\n'
    sendDevicesStr = urlencode({'Devices' : deviceStr, 'UUID' : profile.host.UUID})
    #debug(sendDevicesStr)
    
    try:
        o=grabber.urlopen('%s/addDevices' % smoonURL, data=sendDevicesStr, http_headers=(
                        ('Content-length', '%i' % len(sendDevicesStr)),
                        ('Content-type', 'application/x-www-form-urlencoded')))
    except urlgrabber.grabber.URLGrabError, e:
        error('Error contacting Server: %s' % e)
        return 1
    else:
        serverMessage(o.read())
        o.close()
    
    url = urljoin(smoonURL, '/show?UUID=%s' % profile.host.UUID)
    print 'To view your profile visit: %s' % url
    return 0
    
if retry:
    while 1:
        if not send():
            sys.exit(0)
        error("Retry Enabled - Retrying")
        time.sleep(5)
else:
    if send():
        print "Could not send - Exiting"
        sys.exit(1)
