from hardware.model.model import *
from hardware.model.views import *

def classes_report(cls):
    types = top_devices_per_class(type)
    count = hosts_per_class(type)
    vendors = top_vendors_per_class(type)
    return (types, count, vendors)

    
class ByClass(object):
    def __init__(self):
        self.data = {}

    def fetch_data(self):
        classes = all_classes()
        count = {}
        types = {}
        vendors = {}
        total_hosts = 0

        # We only want hosts that detected hardware (IE, hal was working properly)
        total_hosts = host_count_with_devices()
        
        for cls in classes:
            type = cls.cls
            t, c, v = classes_report(type)

            self.data[type] = (total_hosts, c, t, v)

    def __getitem__(self, key):
        return self.data[key]

    pass
