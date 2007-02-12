#!/usr/bin/python

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
