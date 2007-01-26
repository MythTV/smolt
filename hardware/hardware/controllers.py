from turbogears import controllers, expose
import sqlobject
from hardware import model
# import logging
# log = logging.getLogger("hardware.controllers")
from hardware.model import Host
from hardware.model import Device
from hardware.model import HostLinks
from sqlobject import SQLObjectNotFound

class Root(controllers.RootController):
    @expose(template="hardware.templates.welcome")
    def index(self):
        import time
        # log.debug("Happy TurboGears Controller Responding For Duty")
        return dict(now=time.ctime())

    @expose(template="hardware.templates.add")
    def add(self, UUID, lsbRelease, OS, platform, bogomips, systemMemory, systemSwap, CPUVendor, numCPUs, CPUSpeed, language, defaultRunlevel, vendor, system):
        import time
        UUID = UUID.rstrip()

        try:
            Host._connection.queryAll("delete from host_links where host_u_u_id='%s'" % UUID)
        except:
            DoNothing = 1

        try:
            hostSQL = Host.byUUID(UUID)
            hostSQL.lsbRelease = lsbRelease.rstrip()
            hostSQL.OS = OS.rstrip()
            hostSQL.platform = platform.rstrip()
            try:
                hostSQL.bogomips = float(bogomips)
            except:
                hostSQL.bogomips = 0
            hostSQL.systemMemory = int(systemMemory)
            hostSQL.systemSwap = int(systemSwap)
            hostSQL.CPUVendor = CPUVendor.rstrip()
            hostSQL.numCPUs = int(numCPUs)
            hostSQL.CPUSpeed = float(CPUSpeed)
            hostSQL.language = language.rstrip()
            hostSQL.defaultRunlevel = int(defaultRunlevel)
            hostSQL.vendor = vendor.rstrip()
            hostSQL.system = system.rstrip()

        except SQLObjectNotFound:
            hostSQL = Host(UUID = UUID,
                        lsbRelease = lsbRelease.rstrip(),
                        OS = OS.rstrip(),
                        platform = platform.rstrip(),
                        bogomips = float(bogomips),
                        systemMemory = int(systemMemory),
                        systemSwap = int(systemSwap),
                        CPUVendor = CPUVendor.rstrip(),
                        numCPUs = int(numCPUs),
                        CPUSpeed = float(CPUSpeed),
                        language = language.rstrip(),
                        defaultRunlevel = int(defaultRunlevel),
                        vendor = vendor.rstrip(),
                        system = system.rstrip())

        return dict(hostObject=hostSQL)

    @expose(template="hardware.templates.device")
    def addDevice(self, UUID, Description, Bus, Driver, Class):
        import time
        from mx import DateTime
        UUID = UUID.rstrip()
        Description = Description.rstrip()
        Bus = Bus.rstrip()
        Driver = Driver.rstrip()
        Class = Class.rstrip()

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
        stats['OStot'] = Host._connection.queryAll("Select count(o_s) from Host")[0][0]

        stats['runlevel'] = Host._connection.queryAll("Select default_runlevel, count(default_runlevel) as cnt from Host group by default_runlevel order by cnt desc")
        stats['runleveltot'] = Host._connection.queryAll("Select count(default_runlevel) from Host")[0][0]

        stats['devices'] = Host._connection.queryAll("select Device.description, count(host_links.device_id) as cnt from host_links, Device where host_links.Device_id=Device.id group by host_links.device_id order by cnt desc limit 20;")
        stats['devices20sum'] = Host._connection.queryAll("select count(*) as cnt from host_links, Device where host_links.Device_id=Device.id order by cnt desc limit 20;")[0][0]
        stats['devicestot'] = Host._connection.queryAll("Select count(*) from host_links")[0][0]

        stats['numCPUs'] = Host._connection.queryAll("Select num_cp_us, count(num_cp_us) as cnt from Host group by num_cp_us order by cnt desc")
        stats['numCPUstot'] = int(Host._connection.queryAll('Select count(num_cp_us) from Host;')[0][0])

        stats['cpuVendor'] = Host._connection.queryAll("Select cpu_vendor, count(cpu_vendor) as cnt from Host group by cpu_vendor order by cnt desc")
        stats['cpuVendortot'] = int(Host._connection.queryAll('Select count(cpu_vendor) from Host;')[0][0])
 
        stats['language'] = Host._connection.queryAll("Select language, count(language) as cnt from Host group by language order by cnt desc")
        stats['languagetot'] = int(Host._connection.queryAll('Select count(language) from Host;')[0][0])
 
        stats['sysMem'] = []
        stats['sysMem'].append(Host._connection.queryAll('select (select "< 512") as range, count(system_memory) as cnt from Host where system_memory <= 512')[0])
        stats['sysMem'].append(Host._connection.queryAll('select (select "513 - 1024") as range, count(system_memory) as cnt from Host where system_memory > 512 and system_memory <= 1024')[0])
        stats['sysMem'].append(Host._connection.queryAll('select (select "1025 - 2048") as range, count(system_memory) as cnt from Host where system_memory > 1025 and system_memory <= 2048')[0])
        stats['sysMem'].append(Host._connection.queryAll('select (select "> 2048") as range, count(system_memory) as cnt from Host where system_memory > 2048')[0])

        stats['swapMem'] = []
        stats['swapMem'].append(Host._connection.queryAll('select (select "< 512") as range, count(system_swap) as cnt from Host where system_swap <= 512')[0])
        stats['swapMem'].append(Host._connection.queryAll('select (select "513 - 1024") as range, count(system_swap) as cnt from Host where system_swap > 512 and system_swap <= 1024')[0])
        stats['swapMem'].append(Host._connection.queryAll('select (select "1025 - 2048") as range, count(system_swap) as cnt from Host where system_swap > 1025 and system_swap <= 2048')[0])
        stats['swapMem'].append(Host._connection.queryAll('select (select "> 2048") as range, count(system_swap) as cnt from Host where system_swap > 2048')[0])

        stats['cpuSpeed'] = []
        stats['cpuSpeed'].append(Host._connection.queryAll('select (select "=< 512") as range, count(cpu_speed) as cnt from Host where cpu_speed <= 512')[0])
        stats['cpuSpeed'].append(Host._connection.queryAll('select (select "513 - 1024") as range, count(cpu_speed) as cnt from Host where cpu_speed > 512 and cpu_speed <= 1024')[0])
        stats['cpuSpeed'].append(Host._connection.queryAll('select (select "1025 - 2048") as range, count(cpu_speed) as cnt from Host where cpu_speed > 1025 and cpu_speed <= 2048')[0])
        stats['cpuSpeed'].append(Host._connection.queryAll('select (select "> 2048") as range, count(cpu_speed) as cnt from Host where cpu_speed > 2048')[0])
 
        stats['bogomips'] = []
        stats['bogomips'].append(Host._connection.queryAll('select (select "=< 512") as range, count(bogomips) as cnt from Host where bogomips <= 512')[0])
        stats['bogomips'].append(Host._connection.queryAll('select (select "513 - 1024") as range, count(bogomips) as cnt from Host where bogomips > 512 and bogomips <= 1024')[0])
        stats['bogomips'].append(Host._connection.queryAll('select (select "1025 - 2048") as range, count(bogomips) as cnt from Host where bogomips > 1025 and bogomips <= 2048')[0])
        stats['bogomips'].append(Host._connection.queryAll('select (select "> 2048") as range, count(bogomips) as cnt from Host where bogomips > 2048')[0])
 
 

#    id INTEGER PRIMARY KEY,
#    u_u_id TEXT NOT NULL UNIQUE,
#    lsb_release TEXT,
#    o_s TEXT,
#    platform TEXT,
#    bogomips FLOAT,
#    system_memory INT,
#    system_swap INT,
#    vendor TEXT,
#    system TEXT,
#    cpu_vendor TEXT,
#    num_cp_us INT,
#    cpu_speed TEXT,
#    language TEXT,
#    default_runlevel INT


        return dict(Host=Host, Device=Device, HostLinks=HostLinks, Stat=stats)


