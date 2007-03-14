#!/usr/bin/python

# smolt - Fedora hardware profiler
#
# Copyright (C) 2007 Mike McGrath
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import sys
from optparse import OptionParser
import time
from urlparse import urljoin
import os

sys.path.append('/usr/share/smolt/client')

from i18n import _
import smolt
from smolt import debug
from smolt import error

parser = OptionParser(version = smolt.smoltProtocol)

parser.add_option('-d', '--debug',
                  dest = 'DEBUG',
                  default = False,
                  action = 'store_true',
                  help = _('enable debug information'))
parser.add_option('-s', '--server',
                  dest = 'smoonURL',
                  default = smolt.smoonURL,
                  metavar = 'smoonURL',
                  help = _('specify the URL of the server (default "%default")'))
parser.add_option('-p', '--printOnly',
                  dest = 'printOnly',
                  default = False,
                  action = 'store_true',
                  help = _('print information only, do not send'))
parser.add_option('-a', '--autoSend',
                  dest = 'autoSend',
                  default = False,
                  action = 'store_true',
                  help = _('don\'t prompt to send, just send'))
parser.add_option('-r', '--retry',
                  dest = 'retry',
                  default = False,
                  action = 'store_true',
                  help = _('continue to send until success'))
parser.add_option('-u', '--useragent', '--user_agent',
                  dest = 'user_agent',
                  default = smolt.user_agent,
                  metavar = 'USERAGENT',
                  help = _('specify HTTP user agent (default "%default")'))
parser.add_option('-t', '--timeout',
                  dest = 'timeout',
                  type = 'float',
                  default = smolt.timeout,
                  help = _('specify HTTP timeout in seconds (default %default seconds)'))
parser.add_option('-c', '--checkin',
                  dest = 'checkin',
                  default = False,
                  action = 'store_true',
                  help = _('Automated Checkin'))

(opts, args) = parser.parse_args()

smolt.DEBUG = opts.DEBUG

if opts.checkin and os.path.exists('/var/lock/subsys/smolt'):
    # Smolt is set to run
    opts.autoSend = True
elif opts.checkin:
    # Tried to check in but checkins are disabled
    print _('Smolt set to checkin but checkins are disabled (hint: service smolt start)')
    sys.exit(6)

# read the profile
try:
    profile = smolt.Hardware()
except smolt.SystemBusError, e:
    error('Error: %s' % e)
    error('\tHint: Try "service haldaemon start"')
    sys.exit(8)
print profile.getProfile()

if not opts.autoSend:
    if opts.printOnly:
        sys.exit(0)
    else:
        send = raw_input("\nSend this information to the Smolt server? (y/n) ")
        if send.lower() != 'y':
            error('Exiting...')
            sys.exit(4)
    
if opts.retry:
    while 1:
        if not profile.send(user_agent=opts.user_agent, smoonURL=opts.smoonURL, timeout=opts.timeout):
            sys.exit(0)
        error(_('Retry Enabled - Retrying'))
        time.sleep(5)
else:
    if profile.send(user_agent=opts.user_agent, smoonURL=opts.smoonURL, timeout=opts.timeout):
        print _('Could not send - Exiting')
        sys.exit(1)

url = urljoin(opts.smoonURL, '/show?UUID=%s' % profile.host.UUID)
print _('To view your profile visit: %s') % url
