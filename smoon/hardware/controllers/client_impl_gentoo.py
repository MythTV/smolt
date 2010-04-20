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

import copy
from hardware.controllers.client_impl import ClientImplementation
from turbogears.database import session

# TODO move files, resolve hack
import os
import sys
import inspect
sys.path.append(os.path.join(os.path.dirname(inspect.currentframe().f_code.co_filename), '..'))
from play import handle_gentoo_data

class GentooClientImplementation(ClientImplementation):
    def data_for_next_hop(self, host_dict):
        deep_copy = copy.copy(host_dict)
        try:
            del deep_copy['distro_specific']['gentoo']
            if not deep_copy['distro_specific']:
                del deep_copy['distro_specific']
        except KeyError:
            pass
        return deep_copy

    def extend_host_sql_hook(self, host_sql, host_dict):
        handle_gentoo_data(session, host_dict, host_sql.id)
        return host_sql
