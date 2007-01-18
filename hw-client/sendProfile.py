#!/usr/bin/python

import hardware
import sys
import os
import commands

UUIDcmd = commands.getstatusoutput('/bin/cat /etc/sysconfig/hw-uuid')

if(UUIDcmd[0] == 0):
    UUID = UUIDcmd[1]
else:
    UUID = commands.getstatusoutput('/bin/cat /proc/sys/kernel/random/uuid> /tmp/hw-uuid; cat /tmp/hw-uuid')[1]

hw = hardware.Hardware()
lsbRelease = commands.getstatusoutput('/usr/bin/lsb_release')[1]
OS = commands.getstatusoutput('/bin/cat /etc/redhat-release')[1]
defaultRunlevel = commands.getstatusoutput('/bin/grep :initdefault: /etc/inittab')[1].split(':')[1]
language = commands.getstatusoutput('echo $LANG')[1]
platform = bogomips = CPUVendor = numCPUs = CPUSpeed = systemMemory = systemSwap = vendor = system = ''
for device in hw:
    try:
        platform = device['platform']
        bogomips = device['bogomips']
        CPUVendor = "%s - %s" % (device['type'], device['model'])
        numCPUs = device['count']
        CPUSpeed = device['speed']
    except:
        N = ''
    try:
        systemMemory = device['ram']
        systemSwap = device['swap']
    except:
        N = ''
    try:
        vendor = device['vendor']
        system = device['system']
    except:
        N = ''

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

commands.getstatusoutput('/usr/bin/wget -O /dev/null -q http://publictest4.fedora.redhat.com/add --post-data="%s"' % sendHostStr)[1]
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
        commands.getstatusoutput('/usr/bin/wget -O /dev/null -q http://publictest4.fedora.redhat.com/addDevice --post-data="%s"' % sendDeviceStr)[1]

print 'Thankyou, your uuid (in /etc/sysconfig/hw-uuid, is %s)' % UUID
