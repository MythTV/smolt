from sqlobject import *
from datetime import datetime
from turbogears.database import PackageHub
from turbogears.identity.soprovider import TG_User, TG_Group, TG_Permission

hub = PackageHub("hardware")
__connection__ = hub

''' Now storing device ID.  This was added because description can change 
    over time.  Unfortunately not everything has a device ID.  This is nasty
    but since we are storing both we can figure out what to do later'''

class Device(SQLObject):
    Description = UnicodeCol(title="Device",alternateID=True,length=128)
    Bus = StringCol(title="Bus")
    Driver = StringCol(title="Module / Driver")
    Class = StringCol()
    DateAdded = DateTimeCol(title="Date Added")
    DeviceId = StringCol(title='Device ID', length=16)  #Format: Vendor:Device
    VendorId = IntCol()
    SubsysVendorId = IntCol()
    SubsysDeviceId = IntCol()

class HostLinks(SQLObject):
    hostLink = ForeignKey('Host')
#    hostUUID = UnicodeCol(title="Host",length=36,alternateID=True)
    deviceID = IntCol(title="Device Link")
#    deviceID = MultipleJoin('Device', joinColumn='id')

class Host(SQLObject):
    UUID = UnicodeCol(title="UUID",alternateID=True,unique=True,notNone=True,length=36)
    OS = StringCol()
    platform = StringCol()
    bogomips = FloatCol()
    systemMemory = IntCol(title="System Memory")
    systemSwap = IntCol(title="System Swap Memory")
    vendor = StringCol(title="Machine Vendor")
    system = StringCol(title="Machine Model")
    CPUVendor = StringCol(title="CPU Vendor")
    CPUModel = StringCol(title="CPU Model")
    numCPUs = IntCol(title="Number of CPUs")
    CPUSpeed = FloatCol(title="CPU Speed")
    language = StringCol(title="Language")
    kernelVersion = StringCol(title="Kernel")
    formfactor = StringCol(title="Formfactor")
    defaultRunlevel = IntCol(title="Default Runlevel")
    selinux_enabled = BoolCol(title="SELinux Enabled")
    selinux_enforce = StringCol(title="SELinux Enforce")
    hostLink = MultipleJoin('HostLinks', joinColumn='host_link_id')
    lastModified = DateTimeCol(title="Last Modified")

class FasLink(SQLObject):
    UUID = UnicodeCol(title="UUID",alternateID=True,unique=True,notNone=True,length=36)
    userName = StringCol(alternateID=True)
