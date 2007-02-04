from sqlobject import *
from datetime import datetime
from turbogears.database import PackageHub
from turbogears.identity.soprovider import TG_User, TG_Group, TG_Permission

hub = PackageHub("hardware")
__connection__ = hub

class Device(SQLObject):
    Description = StringCol(title="Device",alternateID=True)
    Bus = StringCol(title="Bus")
    Driver = StringCol(title="Module / Driver")
    Class = StringCol()
    DateAdded = DateTimeCol(title="Date Added")


class HostLinks(SQLObject):
    hostUUID = ForeignKey("Host")
    deviceID = IntCol(title="Device Link")


class Host(SQLObject):
    UUID = StringCol(title="UUID",alternateID=True,unique=True,notNone=True)
    lsbRelease = StringCol()
    OS = StringCol()
    platform = StringCol()
    bogomips = FloatCol()
    systemMemory = IntCol(title="System Memory")
    systemSwap = IntCol(title="System Swap Memory")
    vendor = StringCol(title="Machine Vendor")
    system = StringCol(title="Machine Model")
    CPUVendor = StringCol(title="CPU Vendor")
    numCPUs = IntCol(title="Number of CPUs")
    CPUSpeed = FloatCol(title="CPU Speed")
    language = StringCol(title="Language")
    defaultRunlevel = IntCol(title="Default Runlevel")



