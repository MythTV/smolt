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
import random
import getpass

sys.path.append('/usr/share/smolt/client')

from i18n import _
import smolt
from smolt import debug
from smolt import error
from scan import scan

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
parser.add_option('--username',
                  dest = 'userName',
                  default = None,
                  metavar = 'userName',
                  help = _('(optional) Fedora Account System registration'))
parser.add_option('--password',
                  dest = 'password',
                  default = None,
                  metavar = 'password',
                  help = _('password, will prompt if not specified'))
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
                  help = _('this is an automated checkin, will only run if the "smolt" service has been started'))
parser.add_option('-S', '--scanOnly',
                  dest = 'scanOnly',
                  default = False,
                  action = 'store_true',
                  help = _('only scan this machine for known hardware errata, do not send profile.'))
parser.add_option('--submitOnly',
                  dest = 'submitOnly',
                  default = False,
                  action = 'store_true',
                  help = _('do not scan this machine for know hardware errata, only submit profile.'))
parser.add_option('--uuidFile',
                  dest = 'uuidFile',
                  default = smolt.hw_uuid_file,
                  help = _('specify which uuid to use, useful for debugging and testing mostly.'))
parser.add_option('-b', '--bodhi',
                  dest = 'bodhi',
                  default = False,
                  action = 'store_true',
                  help = _('Submit this profile to Bodhi as well, for Fedora Developmnent'))


(opts, args) = parser.parse_args()

smolt.DEBUG = opts.DEBUG
smolt.hw_uuid_file = opts.uuidFile

if opts.checkin and os.path.exists('/var/lock/subsys/smolt'):
    # Smolt is set to run
    opts.autoSend = True
elif opts.checkin:
    # Tried to check in but checkins are disabled
    print _('Smolt set to checkin but checkins are disabled (hint: service smolt start)')
    sys.exit(6)

# read the profile
profile = smolt.get_profile()
    
if opts.scanOnly:
    scan(profile)
    sys.exit(0)

for line in profile.getProfile():
    print line

if not opts.autoSend:
    if opts.printOnly:
        sys.exit(0)
    else:
        try:
            send = raw_input('\n' + 
                             _('Send this information to the Smolt server? (y/n)') + ' ')
            if send[:1].lower() != _('y'):
                error(_('Exiting...'))
                sys.exit(4)
        except KeyboardInterrupt:
            error(_('Exiting...'))
            sys.exit(4)
    
if opts.retry:
    while 1:
        result, pub_uuid = profile.send(user_agent=opts.user_agent, 
                              smoonURL=opts.smoonURL, 
                              timeout=opts.timeout) 
        if not result:
            sys.exit(0)
        error(_('Retry Enabled - Retrying'))
        time.sleep(30)
else:
    result, pub_uuid, admin = profile.send(user_agent=opts.user_agent, 
                                    smoonURL=opts.smoonURL, 
                                    timeout=opts.timeout)
    if result:
        print _('Could not send - Exiting')
        sys.exit(1)

if opts.userName: 
    if not opts.password:
        password = getpass.getpass('\n' + _('Password:') + ' ')
    else:
        password = opts.password

    if profile.register(userName=opts.userName, password=password, user_agent=opts.user_agent, smoonURL=opts.smoonURL, timeout=opts.timeout):
        print _('Registration Failed, Try again')
if not opts.submitOnly:
    scan(profile)
pubUrl = smolt.get_profile_link(opts.smoonURL, pub_uuid)
print

print _('To share your profile: \n\t%s (public)') % pubUrl
if not smolt.secure:
    print _('\tAdmin Password: %s') % admin
