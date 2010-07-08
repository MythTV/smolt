# Copyright (C) 2010 Sebastian Dziallas
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
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#

import os
import linecache
import subprocess
from gettext import gettext as _

_not_available = _('Not available')

def submit_profile():
    subprocess.call(['smoltSendProfile', '-a'])

def delete_profile():
    subprocess.call(['smoltDeleteProfile'])
    os.remove(os.getenv("HOME") + '/.smolt/uuiddb.cfg')

def get_profile_url():
    uuiddb = os.getenv("HOME") + '/.smolt/uuiddb.cfg'
    if os.path.exists(uuiddb):
        database = linecache.getline(uuiddb, 2)
        profile = database[55:]
        profile_url = 'http://www.smolts.org/client/show/' + profile
    else:
        profile_url = _not_available
    return profile_url
    
def print_profile_url():
    profile_url = get_profile_url()
    if profile_url is None:
        profile_url = _not_available
    print profile_url

def _read_file(path):
    if os.access(path, os.R_OK) == 0:
        return None

    fd = open(path, 'r')
    value = fd.read()
    fd.close()
    if value:
        value = value.strip('\n')
        return value
    else:
        _logger.debug('No information in file or directory: %s', path)
        return None

def get_policy():

    policy_file = os.path.join('/usr/share/smolt/doc/', 'PrivacyPolicy')

    try:
        fd = open(policy_file)
        # remove 0x0c page breaks which can't be rendered in text views
        policy_text = fd.read().replace('\x0c', '')
        fd.close()
    except IOError:
        policy_text = _not_available
    return policy_text
