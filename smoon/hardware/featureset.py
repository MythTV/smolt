# -*- coding: utf-8 -*-
# smolt - Fedora hardware profiler
#
# Copyright (C) 2010 Sebastian Pipping <sebastian@pipping.org>
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
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301, USA.


_FINAL_SERVER_KEY = 'smolts.org'
MYTH_TV = 'smolt.mythvantage.com'
GENTOO = 'smolt.gentoo.org'

_VALID_FEATURE_SET_KEYS = (
    _FINAL_SERVER_KEY,
    MYTH_TV,
    GENTOO
)

_initialized = False
_feature_set_key = None
_config_filename = None


def this_is(feature_set_key):
    global _initialized
    assert(_initialized)

    global _feature_set_key
    return _feature_set_key == feature_set_key


def at_final_server():
    global _initialized
    assert(_initialized)

    global _feature_set_key
    global _FINAL_SERVER_KEY
    return _feature_set_key == _FINAL_SERVER_KEY


def make_client_impl(smolt_protocol=None, token=None):
    global _initialized
    assert(_initialized)

    global MYTH_TV
    global GENTOO
    if this_is(MYTH_TV):
        from hardware.controllers.client_impl_mythtv import MythTvClientImplementation
        impl = MythTvClientImplementation(smolt_protocol, token)
    elif this_is(GENTOO):
        from hardware.controllers.client_impl_gentoo import GentooClientImplementation
        impl = GentooClientImplementation(smolt_protocol, token)
    else:
        from hardware.controllers.client_impl import ClientImplementation
        impl = ClientImplementation(smolt_protocol, token)
    return impl


def forward_url():
    global _initialized
    assert(_initialized)
    assert(not at_final_server())
    return 'http://smolts.org/'


def config_filename():
    global _initialized
    assert(_initialized)

    global _config_filename
    return _config_filename


def init(config_filename=None):
    global _initialized
    assert(not _initialized)
    _initialized = True

    import sys
    import os
    from ConfigParser import ConfigParser, NoOptionError

    global _config_filename
    if config_filename is None:
        smoon_location = os.path.join(os.path.dirname(__file__), "..")
        if os.path.exists(os.path.join(smoon_location, "setup.py")):
            basename = 'dev.cfg'
        else:
            basename = 'prod.cfg'
        _config_filename = os.path.normpath(os.path.join(smoon_location, basename))
    else:
        _config_filename = config_filename
    
    config = ConfigParser()
    config.read(_config_filename)
    section = 'global'
    key = 'feature_set_key'
    global _feature_set_key
    try:
        _feature_set_key = config.get(section, key)
    except NoOptionError:
        sys.stderr.write('Config file "%s" is missing required key "%s" in section "%s".\n' % (_config_filename, key, section))
        sys.stderr.write('Example values include %s.\n' % ', '.join('"%s"' % e for e in _VALID_FEATURE_SET_KEYS))
        sys.exit(1)

    _feature_set_key = _feature_set_key.lstrip('"\'').rstrip('"\'')
    if _feature_set_key not in _VALID_FEATURE_SET_KEYS:
        sys.stderr.write('Config key "%s" in section "%s" has invalid value "%s".\n' % (key, section, feature_set_key))
        sys.stderr.write('Example values include %s.\n' % ', '.join('"%s"' % e for e in _VALID_FEATURE_SET_KEYS))
        sys.exit(1)
