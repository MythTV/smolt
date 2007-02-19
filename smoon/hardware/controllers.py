from turbogears import controllers, expose
import sqlobject
from hardware import model
# import logging
# log = logging.getLogger("hardware.controllers")
from hardware.model import Host
from hardware.model import Device
from hardware.model import HostLinks
from sqlobject import SQLObjectNotFound
from turbogears import exception_handler

# This is such a bad idea, yet here it is.
CRYPTPASS = ''


class Root(controllers.RootController):
    @expose(template="hardware.templates.welcome")
    def index(self):
        import time
        # log.debug("Happy TurboGears Controller Responding For Duty")
        return dict(now=time.ctime())

    @expose(template="hardware.templates.error")
    def errorClient(self, tg_exceptions=None):
        ''' Exception handler, Sends messages back to the client'''
        message = 'ServerMessage: %s' % tg_exceptions
        return dict(handling_value=True,exception=message)

    @expose(template="hardware.templates.error")
    def errorWeb(self, tg_exceptions=None):
        ''' Exception handler, Sends messages back to the client'''
        message = 'Error: %s' % tg_exceptions
        return dict(handling_value=True,exception=message)



    @expose(template="hardware.templates.show")
    @exception_handler(errorWeb,rules="isinstance(tg_exceptions,ValueError)")
    def show(self, UUID=''):
            try:
                UUID = u'%s' % UUID.strip()
                UUID = UUID.encode('utf8')
            except:
                raise ValueError("Critical: Unicode Issue - Tell Mike!")

            try:
                hostObject = Host.byUUID(UUID)
            except:
                raise ValueError("Critical: UUID Not Found - %s" % UUID)
            devices = []
            for dev in hostObject.hostLink:
                devices.append(Device.select('id=%s' % dev.deviceID)[0])
            return dict(hostObject=hostObject, devices=devices)

    @expose(template="hardware.templates.delete")
    @exception_handler(errorClient,rules="isinstance(tg_exceptions,ValueError)")
    def delete(self, UUID=''):
        try:
            host = Host.byUUID(UUID)
        except:
            raise ValueError("Critical: UUID does not exist %s " % UUID)
        try:
            Host._connection.queryAll("delete from host_links where host_link_id='%s';" % host.id)
            Host._connection.queryAll("delete from host where '%s';" % host.id)
        except:
            raise ValueError("Critical: Could not delete UUID - Please contact the smolt development team")
        raise ValueError('Success: UUID Removed')

    @expose(template="hardware.templates.token")
    def token(self, UUID):
        from Crypto.Cipher import XOR
        import urllib
        import time, datetime

        crypt = XOR.new(CRYPTPASS)
        str = "%s\n%s " % ( int(time.mktime(datetime.datetime.now().timetuple())), UUID)
        # I hate obfuscation.  Its all I've got
        token = crypt.encrypt(str)
        return dict(token=urllib.quote(token))

    @expose(template="hardware.templates.show")
    @exception_handler(errorClient,rules="isinstance(tg_exceptions,ValueError)")
    def add(self, UUID, OS, platform, bogomips, systemMemory, systemSwap, CPUVendor, numCPUs, CPUSpeed, language, defaultRunlevel, vendor, system, token, lsbRelease='Depricated', CPUModel='PleaseUpgradeSmolt'):
        from Crypto.Cipher import XOR
        import urllib
        import time, datetime

        token = urllib.unquote(token)
        crypt = XOR.new(CRYPTPASS)
        tokenPlain = crypt.decrypt(token).split('\n')
        tokenTime = int(tokenPlain[0])
        tokenUUID = tokenPlain[1]
        currentTime = int(time.mktime(datetime.datetime.now().timetuple()))
        if currentTime - tokenTime > 20:
            raise ValueError("Critical: Invalid Token")
        if UUID.strip() != tokenUUID.strip():
            raise ValueError("Critical: Invalid Token")

        UUID = UUID.strip()
        try:
            hostSQL = Host.byUUID(UUID)
            Host._connection.queryAll("delete from host_links where host_link_id='%s'" % hostSQL.id)

            hostSQL.OS = OS.strip()
            hostSQL.platform = platform.strip()
            try:
                hostSQL.bogomips = float(bogomips)
            except:
                hostSQL.bogomips = 0
            hostSQL.systemMemory = int(systemMemory)
            hostSQL.systemSwap = int(systemSwap)
            hostSQL.CPUVendor = CPUVendor.strip()
            hostSQL.CPUModel = CPUModel.strip()
            hostSQL.numCPUs = int(numCPUs)
            hostSQL.CPUSpeed = float(CPUSpeed)
            hostSQL.language = language.strip()
            hostSQL.defaultRunlevel = int(defaultRunlevel)
            hostSQL.vendor = vendor.strip()
            hostSQL.system = system.strip()

        except SQLObjectNotFound:
            try:
                bogomips = float(bogomips)
            except:
                bogomips = 0
            hostSQL = Host(UUID = UUID,
                        OS = OS.strip(),
                        platform = platform.strip(),
                        bogomips = float(bogomips),
                        systemMemory = int(systemMemory),
                        systemSwap = int(systemSwap),
                        CPUVendor = CPUVendor.strip(),
                        CPUModel = CPUModel.strip(),
                        numCPUs = int(numCPUs),
                        CPUSpeed = float(CPUSpeed),
                        language = language.strip(),
                        defaultRunlevel = int(defaultRunlevel),
                        vendor = vendor.strip(),
                        system = system.strip())

        return dict(hostObject=hostSQL, devices=[])

    @expose(template="hardware.templates.device")
    @exception_handler(errorClient,rules="isinstance(tg_exceptions,ValueError)")
    def addDevices(self, UUID, Devices):
        import time
        from mx import DateTime
        try:
            host = Host.byUUID(UUID)
        except SQLObjectNotFound:
            raise ValueError("Critical: UUID not found - %s" % UUID)

        for device in Devices.split('\n'):
            if not device:
                continue
            try:
                (VendorID, 
                DeviceID,
                Bus,
                Driver,
                Class,
                Description) = device.split('|')
                DeviceID = '%s:%s' % (DeviceID.strip(), VendorID.strip())
            except:
                raise ValueError("Critical: Device Read Failed - %s" % device)
            try:
                deviceSQL = Device.byDescription(Description)
            except SQLObjectNotFound:
                deviceSQL = Device(Description = Description,
                            Bus = Bus,
                            Driver = Driver,
                            Class = Class,
                            DeviceId = DeviceID,
                            DateAdded = DateTime.now())
            deviceSQL.DeviceId = DeviceID
            link = HostLinks(deviceID=deviceSQL.id, hostLink=host.id)

        return dict(deviceObject=deviceSQL)

    @expose(template="hardware.templates.device")
    @exception_handler(errorClient,rules="isinstance(tg_exceptions,ValueError)")
    def addDevice(self, UUID, Description, Bus, Driver, Class, VendorID='0x0', DeviceID='0x0'):
        import time
        from mx import DateTime
        try:
            host = Host.byUUID(UUID)
        except SQLObjectNotFound:
            raise ValueError("Critical: UUID not found - %s" % UUID)
        Description = Description.strip()
        Bus = Bus.strip()
        Driver = Driver.strip()
        Class = Class.strip()
        DeviceID = '%s:%s' % (DeviceID.strip(), VendorID.strip())

        try:
            deviceSQL = Device.byDescription(Description)

        except SQLObjectNotFound:
            deviceSQL = Device(Description = Description,
                            Bus = Bus,
                            Driver = Driver,
                            Class = Class,
                            DeviceId = DeviceID,
                            DateAdded = DateTime.now())
        deviceSQL.DeviceId = DeviceID
        link = HostLinks(deviceID=deviceSQL.id, hostLink=host.id)
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
        stats['archs'] = Host._connection.queryAll("Select platform, count(platform) as cnt from host group by platform order by cnt desc")
        stats['archstot'] = int(Host._connection.queryAll('select count(platform) from host;')[0][0])

        stats['OS'] = Host._connection.queryAll("Select o_s, count(o_s) as cnt from host group by o_s order by cnt desc")
        stats['OStot'] = Host._connection.queryAll("Select count(o_s) from host")[0][0]

        stats['runlevel'] = Host._connection.queryAll("Select default_runlevel, count(default_runlevel) as cnt from host group by default_runlevel order by cnt desc")
        stats['runleveltot'] = Host._connection.queryAll("Select count(default_runlevel) from host")[0][0]

#        stats['devices'] = Host._connection.queryAll("select device.description, count(host_links.device_id) as cnt from host_links, device where host_links.device_id=device.id group by host_links.device_id order by cnt desc limit 20;")
#        stats['devices20sum'] = Host._connection.queryAll("select count(*) as cnt from host_links, Device where host_links.Device_id=Device.id order by cnt desc limit 20;")[0][0]
#        stats['devicestot'] = Host._connection.queryAll("Select count(*) from host_links")[0][0]

        stats['numCPUs'] = Host._connection.queryAll("Select num_cp_us, count(num_cp_us) as cnt from host group by num_cp_us order by cnt desc")
        stats['numCPUstot'] = int(Host._connection.queryAll('Select count(num_cp_us) from host;')[0][0])

        stats['vendors'] = Host._connection.queryAll("Select vendor, count(vendor) as cnt from host where vendor != 'Unknown' and vendor != '' group by vendor order by cnt desc limit 15;")
        stats['systems'] = Host._connection.queryAll("Select system, count(system) as cnt from host where system != 'Unknown' and system != '' group by system order by cnt desc limit 15;")

        stats['cpuVendor'] = Host._connection.queryAll("Select cpu_vendor, count(cpu_vendor) as cnt from host group by cpu_vendor order by cnt desc")
        cpuVen = {}

        for stat in stats['cpuVendor']:
            try:
                cpuVen[stat[0].split('-')[0].strip()] = cpuVen[stat[0].split('-')[0].strip()] + 1
            except:
                cpuVen[stat[0].split('-')[0].strip()] = 1

        stats['cpuVendor'] = cpuVen


        stats['cpuVendortot'] = int(Host._connection.queryAll('Select count(cpu_vendor) from host;')[0][0])
 
        stats['language'] = Host._connection.queryAll("Select language, count(language) as cnt from host group by language order by cnt desc limit 15")
        stats['languagetot'] = int(Host._connection.queryAll('Select count(language) from host;')[0][0])
 
        stats['sysMem'] = []
        stats['sysMem'].append(Host._connection.queryAll('select "< 512" as range, count(system_memory) as cnt from host where system_memory <= 512')[0])
        stats['sysMem'].append(Host._connection.queryAll('select "513 - 1024" as range, count(system_memory) as cnt from host where system_memory > 512 and system_memory <= 1024')[0])
        stats['sysMem'].append(Host._connection.queryAll('select "1025 - 2048" as range, count(system_memory) as cnt from host where system_memory > 1025 and system_memory <= 2048')[0])
        stats['sysMem'].append(Host._connection.queryAll('select "> 2048" as range, count(system_memory) as cnt from host where system_memory > 2048')[0])

        stats['swapMem'] = []
        stats['swapMem'].append(Host._connection.queryAll('select "< 512" as range, count(system_swap) as cnt from host where system_swap <= 512')[0])
        stats['swapMem'].append(Host._connection.queryAll('select "513 - 1024" as range, count(system_swap) as cnt from host where system_swap > 512 and system_swap <= 1024')[0])
        stats['swapMem'].append(Host._connection.queryAll('select "1025 - 2048" as range, count(system_swap) as cnt from host where system_swap > 1025 and system_swap <= 2048')[0])
        stats['swapMem'].append(Host._connection.queryAll('select "> 2048" as range, count(system_swap) as cnt from host where system_swap > 2048')[0])

        stats['cpuSpeed'] = []
        stats['cpuSpeed'].append(Host._connection.queryAll('select "=< 512" as range, count(cpu_speed) as cnt from host where cpu_speed <= 512')[0])
        stats['cpuSpeed'].append(Host._connection.queryAll('select "513 - 1024" as range, count(cpu_speed) as cnt from host where cpu_speed > 512 and cpu_speed <= 1024')[0])
        stats['cpuSpeed'].append(Host._connection.queryAll('select "1025 - 2048" as range, count(cpu_speed) as cnt from host where cpu_speed > 1025 and cpu_speed <= 2048')[0])
        stats['cpuSpeed'].append(Host._connection.queryAll('select "> 2048" as range, count(cpu_speed) as cnt from host where cpu_speed > 2048')[0])
 
        stats['bogomips'] = []
        stats['bogomips'].append(Host._connection.queryAll('select "=< 512" as range, count(bogomips) as cnt from host where bogomips <= 512')[0])
        stats['bogomips'].append(Host._connection.queryAll('select "513 - 1024" as range, count(bogomips) as cnt from host where bogomips > 512 and bogomips <= 1024')[0])
        stats['bogomips'].append(Host._connection.queryAll('select "1025 - 2048" as range, count(bogomips) as cnt from host where bogomips > 1025 and bogomips <= 2048')[0])
        stats['bogomips'].append(Host._connection.queryAll('select "2049 - 4000" as range, count(bogomips) as cnt from host where bogomips > 2048 and bogomips <= 4000')[0])
        stats['bogomips'].append(Host._connection.queryAll('select "> 4001" as range, count(bogomips) as cnt from host where bogomips > 4001')[0])

        stats['bogomipsTot'] = float(Host._connection.queryAll('select sum((bogomips * num_cp_us)) as cnt from host where bogomips > 0;')[0][0])
        stats['cpuSpeedTot'] = float(Host._connection.queryAll('select sum((cpu_speed * num_cp_us)) as cnt from host where cpu_speed > 0;')[0][0])

        stats['cpusTot'] = int(Host._connection.queryAll('select sum(num_cp_us) as cnt from host;')[0][0])

        #stats['cpusTot'] = int(
 
 

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


