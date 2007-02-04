#!/usr/bin/python

import sys
import getopt
import urlgrabber.grabber
import Profile

DEBUG = 0
printOnly = 0
smoonURL = 'http://smolt.fedoraproject.org/'

sys.path.append('/usr/share/smolt/client')

def error(message):
    print >> sys.stderr, message

def debug(message):
    if DEBUG == 1:
        print message



def help():
    print "Usage:"
    print "     -h,--help           Display this help menu"
    print "     -d,--debug          Enable debug information"
    print "     -p,--printOnly      Print Information only, do not send"
    print "     -s,--server=        serverUrl (http://yourSmoonServer/"
    sys.exit(2)

try:
    opts, args = getopt.getopt(sys.argv[1:], 'phds:', ['help', 'debug', 'printOnly', 'server='])
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

# read the profile
profile = Profile.Profile()

print 'We are about to send the following information to the Fedora Smolt server:'
print
profile.print_data()

if printOnly:
    sys.exit(0)

print 'Transmitting ...'

grabber = urlgrabber.grabber.URLGrabber()

sendHostStr = profile.get_host_string()

debug('smoon server URL: %s' % smoonURL)
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


for sendDeviceStr in profile.get_device_string():
    debug('Sending device')
    try:
        o=grabber.urlopen('%s/addDevice' % smoonURL, data=sendDeviceStr, http_headers=(('Content-length', '%i' % len(sendDeviceStr)),
                                                                                       ('Content-type', 'application/x-www-form-urlencoded')))
    except urlgrabber.grabber.URLGrabError, e:
        error('Error contacting server: %s' % e)
        sys.exit(1)
    else:
        o.close()

print 'Thank you, your uuid (in /etc/sysconfig/hw-uuid), is %s' % profile.UUID
