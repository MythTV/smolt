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


def request_format():
    format = cherrypy.request.params.get('tg_format', '').lower()
    if not format:
        format = cherrypy.request.headers.get('Accept', 'default').lower()
    return format

class Client(object):
    error = Error()
    def __init__(self, smolt_protocol, token):
        self._impl = ClientImplementation(smolt_protocol, token)

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
        return self._impl.delete(uuid)

    @expose("json")
    @exception_handler(error.error_client,rules="isinstance(tg_exceptions,ValueError)")
    def host_rating(self, vendor, system):
        return self._impl.host_rating(vendor, system)

    @expose("json")
    @exception_handler(error.error_client,rules="isinstance(tg_exceptions,ValueError)")
    def regenerate_pub_uuid(self, uuid):
        return self._impl.regenerate_pub_uuid(uuid)

    @expose(template="hardware.templates.pub_uuid")
    @exception_handler(error.error_client, rules="isinstance(tg_exceptions,ValueError)")
    def add_json(self, uuid, host, token, smolt_protocol):
        return self._impl.add_json(uuid, host, token, smolt_protocol)

    @expose()
    def rate_object(self, *args, **kwargs):
        return self._impl.rate_object(self, *args, **kwargs)

    @expose()
    def batch_add_json(self, uuid, host, token, smolt_protocol):
        return self._impl.batch_add_json(uuid, host, token, smolt_protocol)

    @expose()
    def pub_uuid(self, uuid):
        return self._impl.pub_uuid(uuid)
