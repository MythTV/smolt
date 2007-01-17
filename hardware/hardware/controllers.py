from turbogears import controllers, expose
import sqlobject
from hardware import model
# import logging
# log = logging.getLogger("hardware.controllers")
from hardware.model import Host
from hardware.model import Device
from hardware.model import HostLinks
from sqlobject import SQLObjectNotFound

class statusBar:
    def bar(num, tot):
        for i in range (int( float(num) / tot * 50)):
            print '|'



class Root(controllers.RootController):
    @expose(template="hardware.templates.welcome")
    def index(self):
        import time
        # log.debug("Happy TurboGears Controller Responding For Duty")
        return dict(now=time.ctime())

    @expose(template="hardware.templates.add")
    def add(self, UUID, lsbRelease, OS, platform, bogomips, systemMemory, systemSwap, CPUVendor, numCPUs, CPUSpeed, language, defaultRunlevel, vendor, system):
        import time

        try:
            hostSQL = Host.byUUID(UUID)
            hostSQL.lsbRelease = lsbRelease
            hostSQL.OS = OS
            hostSQL.platform = platform
            try:
                hostSQL.bogomips = float(bogomips)
            except:
                hostSQL.bogomips = 0
            hostSQL.systemMemory = int(systemMemory)
            hostSQL.systemSwap = int(systemSwap)
            hostSQL.CPUVendor = CPUVendor
            hostSQL.numCPUs = int(numCPUs)
            hostSQL.CPUSpeed = CPUSpeed
            hostSQL.language = language
            hostSQL.defaultRunlevel = int(defaultRunlevel)
            hostSQL.vendor = vendor
            hostSQL.system = system

        except SQLObjectNotFound:
            hostSQL = Host(UUID = UUID,
                        lsbRelease = lsbRelease,
                        OS = OS,
                        platform = platform,
                        bogomips = float(bogomips),
                        systemMemory = int(systemMemory),
                        systemSwap = int(systemSwap),
                        CPUVendor = CPUVendor,
                        numCPUs = int(numCPUs),
                        CPUSpeed = CPUSpeed,
                        language = language,
                        defaultRunlevel = int(defaultRunlevel),
                        vendor = vendor,
                        system = system)

        return dict(hostObject=hostSQL)

    @expose(template="hardware.templates.device")
    def addDevice(self, UUID, Description, Bus, Driver, Class):
        import time
        from mx import DateTime

        try:
            deviceSQL = Device.byDescription(Description)

        except SQLObjectNotFound:
            deviceSQL = Device(Description = Description,
                            Bus = Bus,
                            Driver = Driver,
                            Class = Class,
                            DateAdded = DateTime.now())

        link = HostLinks(hostUUID=UUID, deviceID=deviceSQL.id)

        return dict(deviceObject=deviceSQL)

    @expose(template="hardware.templates.raw")
    def raw(self, UUID=None):
        host = Host
        hosts = host.select('1=1')
        links = HostLinks
        
        return dict(Hosts=hosts, Device=Device, HostLinks=HostLinks)

    @expose(template="hardware.templates.stats")
    def stats(self):
        stats = {}
        stats['archs'] = Host._connection.queryAll("Select platform, count(platform) as cnt from Host group by platform order by cnt desc")
        stats['archstot'] = int(Host._connection.queryAll('select count(platform) from Host;')[0][0])
        stats['OS'] = Host._connection.queryAll("Select o_s, count(o_s) as cnt from Host group by o_s order by cnt desc")
        stats['runlevel'] = Host._connection.queryAll("Select default_runlevel, count(default_runlevel) as cnt from Host group by default_runlevel order by cnt desc")
        stats['devices'] = Host._connection.queryAll("select Device.description, count(host_links.device_id) as cnt from host_links, Device where host_links.Device_id=Device.id group by host_links.device_id order by cnt desc limit 20;")
        return dict(Host=Host, Device=Device, HostLinks=HostLinks, Stat=stats, statusBar=statusBar)


