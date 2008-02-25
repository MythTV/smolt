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
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301, USA.

import dbus

def dbus_get_interface(bus, service, object, interface):
    iface = None
    # dbus-python bindings as of version 0.40.0 use new api
    if getattr(dbus, 'version', (0,0,0)) >= (0,40,0):
        # newer api: get_object(), dbus.Interface()
        proxy = bus.get_object(service, object)
        iface = dbus.Interface(proxy, interface)
    else:
        # deprecated api: get_service(), get_object()
        svc = bus.get_service(service)
        iface = svc.get_object(object, interface)
    return iface

if __name__ == '__main__':
    bus = dbus.SystemBus()
    mgr = dbus_get_interface(bus, 'org.freedesktop.Hal', \
        '/org/freedesktop/Hal/Manager', 'org.freedesktop.Hal.Manager')
    all_dev_lst = mgr.GetAllDevices()
    for udi in all_dev_lst:
        dev = dbus_get_interface(bus, 'org.freedesktop.Hal', udi, \
            'org.freedesktop.Hal.Device')
        props = dev.GetAllProperties()
        # Uh, let's just print what we've got
        print udi
        print props
