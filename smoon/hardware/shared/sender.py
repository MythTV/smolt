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

from hardware.shared.multipartposthandler import MultipartPostHandler
import urllib2
from urlparse import urljoin
import simplejson
from simplejson import JSONDecodeError
import re

_pub_uuid_extractor = re.compile('^\\s*UUID: pub_([0-9a-fA-F-]+)\\s*$', re.MULTILINE)

class Sender(object):
    def __init__(self, home_url):
        self._home_url = home_url

    def url(self):
        return self._home_url

    def send(self, entry_point, **kwargs):
        request_url = urljoin(self._home_url + "/", entry_point, False)
        
        opener = urllib2.build_opener(MultipartPostHandler)
        params = kwargs

        o = opener.open(request_url, kwargs)
        response = o.read()

        try:
            response_dict = simplejson.loads(response)
        except JSONDecodeError, e:
            # Old servers may be passing HTML, not JSON
            response_dict = dict()
            m = _pub_uuid_extractor.search(response)
            if m is not None:
                response_dict['pub_uuid'] = m.group(1)

        return response_dict
