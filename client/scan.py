import smolt
import simplejson, urllib
from i18n import _
import config

def get_config_attr(attr, default=""):
    if hasattr(config, attr):
        return getattr(config, attr)
    else:
        return default

smoonURL = get_config_attr("SMOON_URL", "http://smolts.org/")


def scan(profile):
    print _("Scanning %s for known errata.\n" % smoonURL)
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
    scanURL='%s/w/api.php?action=query&titles=%s&format=json' % (smoonURL, searchDevices)
    r = simplejson.load(urllib.urlopen(scanURL))
    found = []
    for page in r['query']['pages']:
        try:
            r['query']['pages'][page]['id']
            found.append('\t%swiki/%s' % (smoonURL, r['query']['pages'][page]['title']))
        except KeyError:
            pass
    if found:
        print _("Errata Found!")
        for f in found: print "%s" % f
    else:
        print _("No errata found, if this machine is having issues please go to")
        print _("your profile and create a wiki page for the device so others can")
        print _("benefit")
      
if __name__ == "__main__":  
    # read the profile
    try:
        profile = smolt.Hardware()
    except smolt.SystemBusError, e:
        error(_('Error:') + ' ' + e.message)
        if e.hint is not None:
            error('\t' + _('Hint:') + ' ' + e.hint)
        sys.exit(8)
    scan(profile)

