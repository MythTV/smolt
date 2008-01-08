def getDeviceWikiLink(device):
    return '/wiki/%s/%04x/%04x/%04x/%04x' % (device.bus,
                                             int(device.vendor_id or 0),
                                             int(device.device_id or 0),
                                             int(device.subsys_vendor_id or 0),
                                             int(device.subsys_device_id or 0))

def getHostWikiLink(host):
    return '/wiki/System/%s/%s' % (host.vendor, host.system)

def getOSWikiLink(os):
    return '/wiki/OS/%s' % os
