import smolt
import simplejson, urllib

def scan():

    h = smolt.Hardware()
    devices = []
    for VendorID, DeviceID, SubsysVendorID, SubsysDeviceID, Bus, Driver, Type, Description in h.deviceIter():
        if VendorID:
            devices.append('%s/%04x/%04x/%04x/%04x' % (Bus,
                                             int(VendorID or 0),
                                             int(DeviceID or 0),
                                             int(SubsysVendorID or 0),
                                             int(SubsysDeviceID or 0)) )
    searchDevices = 'NULLPAGE'
    for dev in devices:
        searchDevices = "%s|%s" % (searchDevices, dev)
    scanURL='http://smolts.org/w/api.php?action=query&titles=%s&format=json' % searchDevices
    r = simplejson.load(urllib.urlopen(scanURL))

    for page in r['query']['pages']:
        try:
            r['query']['pages'][page]['id']
            print 'http://smolts.org/wiki/%s' % r['query']['pages'][page]['title']
        except KeyError:
            pass
        
scan()
