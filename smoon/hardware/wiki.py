from turbogears import config

wiki_url = config.config.configMap["global"].get("smolt.wiki_url", "http://smolts.org")


def getDeviceWikiLink(device):
    return '%s/wiki/%s/%04x/%04x/%04x/%04x' % (wiki_url,
                                             device.bus,
                                             int(device.vendor_id or 0),
                                             int(device.device_id or 0),
                                             int(device.subsys_vendor_id or 0),
                                             int(device.subsys_device_id or 0))

def getHostWikiLink(host):
    return '%s/wiki/System/%s/%s' % (wiki_url, host.vendor, host.system)

def getOSWikiLink(os):
    return '%s/wiki/OS/%s' % (wiki_url, os)
