#!/usr/bin/python

import sys
import getopt
import time
from urlparse import urljoin

sys.path.append('/usr/share/smolt/client')

import smolt
from smolt import debug
from smolt import error

smoonURL = 'http://smolt.fedoraproject.org/'
smoltProtocol = '.91'
user_agent = 'smolt/%s' % smoltProtocol
timeout = 60.0

DEBUG = 0
printOnly = 0
autoSend = 0
retry = 0

def help():
    print "Usage:"
    print "     -h,--help           Display this help menu"
    print "     -d,--debug          Enable debug information"
    print "     -p,--printOnly      Print Information only, do not send"
    print "     -a,--autoSend       Don't prompt to send, just send"
    print "     -s,--server=        serverUrl (http://yourSmoonServer/)"
    print "     -r,--retry          Continue to send until success"
    print "     -u,--useragent=     Specify HTTP user agent (default '%s')" % user_agent
    print "     -t,--timeout=       Specify HTTP timeout in seconds (default %1.1f seconds)" % timeout
    sys.exit(2)

try:
    opts, args = getopt.getopt(sys.argv[1:], 'phadrs:u:t:', ['help', 'debug', 'printOnly', 'autoSend', 'server=', 'retry', 'useragent=', 'user_agent=', 'timeout='])
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
    if opt in ('-t', '--timeout'):
        timeout = float(arg)
        
# read the profile
profile = smolt.Hardware()
print profile.getProfile()

if not autoSend:
    if printOnly:
        sys.exit(0)
    else:
        send = raw_input("\nSend this information to the Smolt server? (y/n) ")
        if send.lower() != 'y':
            error('Exiting...')
            sys.exit(4)

    
if retry:
    while 1:
        if not profile.send(user_agent=user_agent, smoonURL=smoonURL, timeout=timeout):
            sys.exit(0)
        error("Retry Enabled - Retrying")
        time.sleep(5)
else:
    if profile.send(user_agent=user_agent, smoonURL=smoonURL, timeout=timeout):
        print "Could not send - Exiting"
        sys.exit(1)

url = urljoin(smoonURL, '/show?UUID=%s' % profile.host.UUID)
print 'To view your profile visit: %s' % url
