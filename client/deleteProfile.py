#!/usr/bin/python

import locale
locale.setlocale(locale.LC_ALL, '')

import gettext
gettext.install('smolt', '/usr/share/locale', unicode=1)

import sys
import urlgrabber.grabber
from optparse import OptionParser

sys.path.append('/usr/share/smolt/client')

import smolt
from smolt import error
from smolt import debug

def serverMessage(page):
    for line in page.split("\n"):
        if 'ServerMessage:' in line:
            error('Server Message: "%s"' % line.split('ServerMessage: ')[1])
            if 'Critical' in line:
                sys.exit(3)

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
parser.add_option('-u', '--useragent',
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

grabber = urlgrabber.grabber.URLGrabber(user_agent=opts.user_agent, timeout=opts.timeout)

delHostString = 'UUID=%s' % profile.host.UUID

try:
    o=grabber.urlopen('%s/delete' % opts.smoonURL, data=delHostString, http_headers=(
                    ('Content-length', '%i' % len(delHostString)),
                    ('Content-type', 'application/x-www-form-urlencoded')))
except urlgrabber.grabber.URLGrabError, e:
    sys.stderr.write(_('Error contacting Server:'))
    sys.stderr.write(str(e))
    sys.stderr.write('\n')
    sys.exit(1)
else:
    serverMessage(o.read())
    o.close()

sys.stdout.write(_('Profile removed, please verify at'))
sys.stdout.write(' %s/show?%s\n' % (opts.smoonURL, delHostString))

