#!/usr/bin/python

import locale
locale.setlocale(locale.LC_ALL, '')

import gettext
gettext.install('smolt', '/usr/share/locale', unicode=1)

import sys
from optparse import OptionParser
import time
from urlparse import urljoin

sys.path.append('/usr/share/smolt/client')

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

(opts, args) = parser.parse_args()

smolt.DEBUG = opts.DEBUG

# read the profile
profile = smolt.Hardware()
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
