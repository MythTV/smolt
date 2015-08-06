# -*- coding: utf-8 -*-
# smolt - Fedora hardware profiler
#
# Copyright (C) 2007 Mike McGrath
# Copyright (C) 2009 Sebastian Pipping <sebastian@pipping.org>
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

import simplejson
from simplejson import JSONEncoder
import cherrypy
from turbogears import expose
from turbogears import exception_handler

from hardware.controllers.error import Error
from hardware.shared.sender import Sender
from hardware.featureset import at_final_server, forward_url, make_client_impl


def request_format():
    format = cherrypy.request.params.get('tg_format', '').lower()
    if not format:
        format = cherrypy.request.headers.get('Accept', 'default').lower()
    return format

class Client(object):
    error = Error()
    def __init__(self, smolt_protocol, token):
        self._impl = make_client_impl(smolt_protocol, token)
        #self._sender = None
        if at_final_server():
            self._sender = None
        else:
            self._sender = Sender(forward_url())

    def new_token(self, hardware_uuid):
        return self._sender.new_token(hardware_uuid)

    def forward(self, function_name, **kwargs):
        return self._sender.send('/client/' + function_name, **kwargs)

    @expose(template="hardware.templates.show", allow_json=True)
    @exception_handler(error.error_web,rules="isinstance(tg_exceptions,ValueError)")
    def show(self, uuid='', UUID=None, admin=None):
        return self._impl.show(uuid, UUID, admin)

    @expose(template="hardware.templates.showall", allow_json=True)
    @exception_handler(error.error_web,rules="isinstance(tg_exceptions,ValueError)")
    def show_all(self, uuid='', admin=None):
        return self._impl.show_all(uuid, admin)

    # NOTE: Exposing as (X)HTML for backwards compatibility
    @expose(template="hardware.templates.delete")
    @exception_handler(error.error_client,rules="isinstance(tg_exceptions,ValueError)")
    def delete(self, uuid=''):
        if not at_final_server():
            # TODO handle "UUID unknown"
            # TODO handle "UUID existing but deletion still failed"
            response_dict = self.forward('delete', uuid=uuid)
        return self._impl.delete(uuid)

    @expose("json")
    @exception_handler(error.error_client,rules="isinstance(tg_exceptions,ValueError)")
    def host_rating(self, vendor, system):
        if at_final_server():
            response_dict = self._impl.host_rating(vendor, system)
        else:
            response_dict = self.forward('host_rating', vendor=vendor, system=system)
            # TODO enrich with domain-specific ratings (e.g. mythtv if available)
        return response_dict

    @expose("json")
    @exception_handler(error.error_client,rules="isinstance(tg_exceptions,ValueError)")
    def regenerate_pub_uuid(self, uuid):
        if at_final_server():
            response_dict = self._impl.regenerate_pub_uuid(uuid)
        else:
            response_dict = self.forward('regenerate_pub_uuid', uuid=uuid)
            pub_uuid = response_dict['pub_uuid']
            self._impl.update_pub_uuid(uuid, pub_uuid)
        return response_dict

    # NOTE: Exposing as (X)HTML for backwards compatibility
    @expose(template="hardware.templates.pub_uuid")
    @exception_handler(error.error_client, rules="isinstance(tg_exceptions,ValueError)")
    def add_json(self, uuid, host, token, smolt_protocol):
        pub_uuid = None
        if not at_final_server():
            final_token = self.new_token(uuid)
            host_dict = simplejson.loads(host)
            host_dict_excerpt = self._impl.data_for_next_hop(host_dict)
            json_host_excerpt = JSONEncoder(indent=2, sort_keys=True).encode(host_dict_excerpt)
            response_dict = self.forward('add_json', uuid=uuid, host=json_host_excerpt,
                token=final_token, smolt_protocol=smolt_protocol)
            pub_uuid = response_dict['pub_uuid']
            # TODO handle passwords?
        response_dict = self._impl.add_json_plus_pub_uuid(uuid, pub_uuid, host, token, smolt_protocol)
        return response_dict

    @expose()
    def rate_object(self, *args, **kwargs):  # NOTE: *args not used, keeping for robustness
        if not at_final_server():
            # TODO check if rating is domain-specific or
            # of interested to final server
            self.forward('rate_object', **kwargs)
        return self._impl.rate_object(self, **kwargs)

    @expose()
    def batch_add_json(self, uuid, host, token, smolt_protocol):
        return self._impl.batch_add_json(uuid, host, token, smolt_protocol)

    @expose()
    def pub_uuid(self, uuid):
        if at_final_server():
            response_dict = self._impl.pub_uuid(uuid)
        else:
            response_dict = self.forward('pub_uuid', uuid=uuid)
        return response_dict
