#!/usr/bin/python

import sys
sys.path.append('/usr/share/smolt/client')

import urlgrabber.grabber

import Profile

smoonURL = 'http://smolt.fedoraproject.org/'

# read the profile
profile = Profile.Profile()

print 'We are about to send the following information to the Fedora Smolt server:'
print
profile.print_data()

print 'Transmitting ...'

grabber = urlgrabber.grabber.URLGrabber()

sendHostStr = profile.get_host_string()

o=grabber.urlopen('%s/add' % smoonURL, data=sendHostStr, http_headers=(('Content-length', '%i' % len(sendHostStr)),
                                                                                              ('Content-type', 'application/x-www-form-urlencoded')))
o.close()

print '.'

for sendDeviceStr in profile.get_device_string():
    o=grabber.urlopen('%s/addDevice' % smoonURL, data=sendDeviceStr, http_headers=(('Content-length', '%i' % len(sendDeviceStr)),
                                                                                                          ('Content-type', 'application/x-www-form-urlencoded')))
    o.close()
        
    print '.'

print 'Thank you, your uuid (in /etc/sysconfig/hw-uuid), is %s' % profile.UUID
