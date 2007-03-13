#!/usr/bin/python

import sys
import getopt
import urlgrabber.grabber

sys.path.append('/usr/share/smolt/client')

import smolt

DEBUG = 0
printOnly = 0
smoonURL = 'http://smolt.fedoraproject.org/'

grabber = urlgrabber.grabber.URLGrabber()

def serverMessage(page):
    for line in page.split("\n"):
        if 'ServerMessage:' in line:
            error('Server Message: "%s"' % line.split('ServerMessage: ')[1])
            if 'Critical' in line:
                sys.exit(3)


def error(message):
    print >> sys.stderr, message

def debug(message):
    if DEBUG == 1:
        print message
# read the profile
profile = smolt.Hardware()

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

delHostString = 'UUID=%s' % profile.host.UUID

try:
    o=grabber.urlopen('%s/delete' % smoonURL, data=delHostString, http_headers=(
                    ('Content-length', '%i' % len(delHostString)),
                    ('Content-type', 'application/x-www-form-urlencoded')))
except urlgrabber.grabber.URLGrabError, e:
    error('Error contacting Server: %s' % e)
    sys.exit(1)
else:
    serverMessage(o.read())
    o.close()

print 'Profile Removed, please verify at %s/show?%s' % (smoonURL, delHostString)

