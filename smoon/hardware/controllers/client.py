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

import cherrypy
from turbogears import expose
from turbogears import exception_handler

from hardware.controllers.error import Error
from hardware.controllers.client_impl import ClientImplementation
from hardware.shared.sender import Sender


def request_format():
    format = cherrypy.request.params.get('tg_format', '').lower()
    if not format:
        format = cherrypy.request.headers.get('Accept', 'default').lower()
    return format

class Client(object):
    error = Error()
    def __init__(self, smolt_protocol, token):
        self._impl = ClientImplementation(smolt_protocol, token)
        self._sender = None
        # TODO self._sender = Sender('http://smolts.org/')

    def forward(self, function_name, **kwargs):
        return self._sender.send('/client/' + function_name, **kwargs)

    def at_final_server(self):
        return self._sender is None

    @expose(template="hardware.templates.show", allow_json=True)
    @exception_handler(error.error_web,rules="isinstance(tg_exceptions,ValueError)")
    def show(self, uuid='', UUID=None, admin=None):
        return self._impl.show(uuid, UUID, admin)

    @expose(template="hardware.templates.showall", allow_json=True)
    @exception_handler(error.error_web,rules="isinstance(tg_exceptions,ValueError)")
    def show_all(self, uuid='', admin=None):
        return self._impl.show_all(uuid, admin)

    @expose(template="hardware.templates.delete")
    @exception_handler(error.error_client,rules="isinstance(tg_exceptions,ValueError)")
    def delete(self, uuid=''):
        if not self.at_final_server():
            response_dict = self.forward('delete', uuid=uuid)
        return self._impl.delete(uuid)

    @expose("json")
    @exception_handler(error.error_client,rules="isinstance(tg_exceptions,ValueError)")
    def host_rating(self, vendor, system):
        if self.at_final_server():
            response_dict = self._impl.host_rating(vendor, system)
        else:
            response_dict = self.forward('host_rating', vendor=vendor, system=system)
            # TODO enrich with domain-specific ratings (e.g. mythtv if available)
        return response_dict

    @expose("json")
    @exception_handler(error.error_client,rules="isinstance(tg_exceptions,ValueError)")
    def regenerate_pub_uuid(self, uuid):
        if self.at_final_server():
            response_dict = self._impl.regenerate_pub_uuid(uuid)
        else:
            response_dict = self.forward('regenerate_pub_uuid', uuid=uuid)
            # TODO store public UUID in our DB, too
        return response_dict

    @expose(template="hardware.templates.pub_uuid")
    @exception_handler(error.error_client, rules="isinstance(tg_exceptions,ValueError)")
    def add_json(self, uuid, host, token, smolt_protocol):
        if not self.at_final_server():
            host_excerpt = self._impl.data_for_next_hop(host)
            response_dict = self.forward('add_json', uuid=uuid, host=host_excerpt, token=token,
                smolt_protocol=smolt_protocol)
            # TODO extract pub ID and re-use it
        response_dict = self._impl.add_json(uuid, host, token, smolt_protocol)
        return response_dict

    @expose()
    def rate_object(self, *args, **kwargs):  # NOTE: *args not used, keeping for robustness
        if not self.at_final_server():
            self.forward('rate_object', **kwargs)
        return self._impl.rate_object(self, **kwargs)

    @expose()
    def batch_add_json(self, uuid, host, token, smolt_protocol):
        return self._impl.batch_add_json(uuid, host, token, smolt_protocol)

    @expose()
    def pub_uuid(self, uuid):
        if self.at_final_server():
            response_dict = self._impl.pub_uuid(uuid)
        else:
            response_dict = self.forward('pub_uuid', uuid=uuid)
        return response_dict
