#!/usr/bin/python

######################################################
# GPL
# This class is a basic wrapper for the dbus bindings
# 
# I have completely destroyed this file, it needs some cleanup
# - mmcgrath
######################################################
# TODO
#
# Abstract "type" in device class
# Find out what we're not getting
#

import dbus
import software
import os
from urllib import urlencode

try:
    import locale
except ImportError:
    locale = None


PCI_BASE_CLASS_STORAGE =        1
PCI_CLASS_STORAGE_SCSI =        0
PCI_CLASS_STORAGE_IDE =         1
PCI_CLASS_STORAGE_FLOPPY =      2
PCI_CLASS_STORAGE_IPI =         3
PCI_CLASS_STORAGE_RAID =        4
PCI_CLASS_STORAGE_OTHER =       80

PCI_BASE_CLASS_NETWORK =        2
PCI_CLASS_NETWORK_ETHERNET =    0
PCI_CLASS_NETWORK_TOKEN_RING =  1
PCI_CLASS_NETWORK_FDDI =        2
PCI_CLASS_NETWORK_ATM =         3
PCI_CLASS_NETWORK_OTHER =       80

PCI_BASE_CLASS_DISPLAY =        3
PCI_CLASS_DISPLAY_VGA =         0
PCI_CLASS_DISPLAY_XGA =         1
PCI_CLASS_DISPLAY_3D =          2
PCI_CLASS_DISPLAY_OTHER =       80

PCI_BASE_CLASS_MULTIMEDIA =     4
PCI_CLASS_MULTIMEDIA_VIDEO =    0
PCI_CLASS_MULTIMEDIA_AUDIO =    1
PCI_CLASS_MULTIMEDIA_PHONE =    2
PCI_CLASS_MULTIMEDIA_OTHER =    80

PCI_BASE_CLASS_BRIDGE =         6
PCI_CLASS_BRIDGE_HOST =         0
PCI_CLASS_BRIDGE_ISA =          1
PCI_CLASS_BRIDGE_EISA =         2
PCI_CLASS_BRIDGE_MC =           3
PCI_CLASS_BRIDGE_PCI =          4
PCI_CLASS_BRIDGE_PCMCIA =       5
PCI_CLASS_BRIDGE_NUBUS =        6
PCI_CLASS_BRIDGE_CARDBUS =      7
PCI_CLASS_BRIDGE_RACEWAY =      8
PCI_CLASS_BRIDGE_OTHER =        80

PCI_BASE_CLASS_COMMUNICATION =  7
PCI_CLASS_COMMUNICATION_SERIAL = 0
PCI_CLASS_COMMUNICATION_PARALLEL = 1
PCI_CLASS_COMMUNICATION_MULTISERIAL = 2
PCI_CLASS_COMMUNICATION_MODEM = 3
PCI_CLASS_COMMUNICATION_OTHER = 80

PCI_BASE_CLASS_INPUT =          9
PCI_CLASS_INPUT_KEYBOARD =      0
PCI_CLASS_INPUT_PEN =           1
PCI_CLASS_INPUT_MOUSE =         2
PCI_CLASS_INPUT_SCANNER =       3
PCI_CLASS_INPUT_GAMEPORT =      4
PCI_CLASS_INPUT_OTHER =         80

PCI_BASE_CLASS_SERIAL =         12
PCI_CLASS_SERIAL_FIREWIRE =     0
PCI_CLASS_SERIAL_ACCESS =       1

PCI_CLASS_SERIAL_SSA =          2
PCI_CLASS_SERIAL_USB =          3
PCI_CLASS_SERIAL_FIBER =        4
PCI_CLASS_SERIAL_SMBUS =        5

class Device:
    def __init__(self, props):
        self.UUID = getUUID()
        try:
            self.bus = props['linux.subsystem'].strip()
        except KeyError:
            self.bus = 'Unknown'
        try:
            self.vendorid = hex(props['%s.vendor_id' % self.bus])
        except KeyError:
            self.vendorid = hex(0)
        try:
            self.deviceid = hex(props['%s.product_id' % self.bus])
        except KeyError:
            self.deviceid = hex(0)
        try:
            self.description = props['info.product'].strip()
        except KeyError:
            self.description = 'No Description'
        try:
            self.driver = props['info.linux.driver'].strip()
        except KeyError:
            self.driver = 'Unknown'
        self.type = classify_hal(props)
        self.deviceSendString = urlencode({
                            'UUID' :        self.UUID,
                            'Bus' :         self.bus,
                            'Driver' :      self.driver,
                            'Class' :       self.type,
                            'VendorID' :    self.vendorid,
                            'DeviceID' :    self.deviceid,
                            'Description' : self.description
                            })

class Host:
    def __init__(self, hostInfo):
        cpuInfo = read_cpuinfo()
        memory = read_memory()
        self.UUID = getUUID()
        self.os = software.read_os()
        self.defaultRunlevel = software.read_runlevel()
        self.bogomips = cpuInfo['bogomips']
        self.cpuVendor = cpuInfo['type']
        self.cpuModel = cpuInfo['model']
        self.numCpus = cpuInfo['count']
        self.cpuSpeed = cpuInfo['speed']
        self.systemMemory = memory['ram']
        self.systemSwap = memory['swap']
        try:
            self.language = os.environ['LANG']
        except KeyError:
            self.language = 'Unknown'
        try:
            self.platform = hostInfo['system.kernel.machine']
        except KeyError:
            self.platform = 'Unknown'
        try:
            self.systemVendor = hostInfo['system.vendor']
        except:
            self.systemVendor = 'Unknown'
        try:
            self.systemModel = hostInfo['system.product']
        except:
            self.systemModel = 'Unknown'

class Hardware:
    devices = {}
    def __init__(self):
        systemBus = dbus.SystemBus()
        mgr = self.dbus_get_interface(systemBus, 'org.freedesktop.Hal', '/org/freedesktop/Hal/Manager', 'org.freedesktop.Hal.Manager')
        all_dev_lst = mgr.GetAllDevices()
        for udi in all_dev_lst:
            dev = self.dbus_get_interface(systemBus, 'org.freedesktop.Hal', udi, 'org.freedesktop.Hal.Device')
            props = dev.GetAllProperties()
            self.devices[udi] = Device(props)
            if udi == '/org/freedesktop/Hal/devices/computer':
                self.host = Host(props)
        self.hostSendString = urlencode({
                            'UUID' :            self.host.UUID,
                            'OS' :              self.host.os,
                            'defaultRunlevel':  self.host.defaultRunlevel,
                            'language' :        self.host.language,
                            'platform' :        self.host.platform,
                            'bogomips' :        self.host.bogomips,
                            'CPUVendor' :       self.host.cpuVendor,
                            'CPUModel' :        self.host.cpuModel,
                            'numCPUs':          self.host.numCpus,
                            'CPUSpeed' :        self.host.cpuSpeed,
                            'systemMemory' :    self.host.systemMemory,
                            'systemSwap' :      self.host.systemSwap,
                            'vendor' :          self.host.systemVendor,
                            'system' :          self.host.systemModel
                            })

    def dbus_get_interface(self, bus, service, object, interface):
        iface = None
        # dbus-python bindings as of version 0.40.0 use new api
        if getattr(dbus, 'version', (0,0,0)) >= (0,40,0):
            # newer api: get_object(), dbus.Interface()
            proxy = bus.get_object(service, object)
            iface = dbus.Interface(proxy, interface)
        else:
            # deprecated api: get_service(), get_object()
            svc = bus.get_service(service)
            iface = svc.get_object(object, interface)
        return iface

# From RHN Client Tools

def classify_hal(node):
    # NETWORK
    if node.has_key('net.interface'):
        return 'NETWORK'
    
    if node.has_key('info.product') and node.has_key('info.category'):
        if node['info.category'] == 'input':
            # KEYBOARD <-- do this before mouse, some keyboards have built-in mice
            if 'keyboard' in node['info.product'].lower():
                return 'KEYBOARD'
            # MOUSE
            if 'mouse' in node['info.product'].lower():
                return 'MOUSE'
    
    if node.has_key('pci.device_class'):
        #VIDEO
        if node['pci.device_class'] == PCI_BASE_CLASS_DISPLAY:
            return 'VIDEO'
        #USB
        if (node['pci.device_class'] ==  PCI_BASE_CLASS_SERIAL
                and node['pci.device_subclass'] == PCI_CLASS_SERIAL_USB):
            return 'USB'
        
        if node['pci.device_class'] == PCI_BASE_CLASS_STORAGE: 
            #IDE
            if node['pci.device_subclass'] == PCI_CLASS_STORAGE_IDE:
                return 'IDE'
            #SCSI
            if node['pci.device_subclass'] == PCI_CLASS_STORAGE_SCSI:
                return 'SCSI'
            #RAID
            if node['pci.device_subclass'] == PCI_CLASS_STORAGE_RAID:
                return 'RAID'
        #MODEM
        if (node['pci.device_class'] == PCI_BASE_CLASS_COMMUNICATION 
                and node['pci.device_subclass'] == PCI_CLASS_COMMUNICATION_MODEM):
            return 'MODEM'
        #SCANNER 
        if (node['pci.device_class'] == PCI_BASE_CLASS_INPUT 
                and node['pci.device_subclass'] == PCI_CLASS_INPUT_SCANNER):
            return 'SCANNER'
        
        if node['pci.device_class'] == PCI_BASE_CLASS_MULTIMEDIA: 
            #CAPTURE -- video capture card
            if node['pci.device_subclass'] == PCI_CLASS_MULTIMEDIA_VIDEO:
                return 'CAPTURE'
            #AUDIO
            if node['pci.device_subclass'] == PCI_CLASS_MULTIMEDIA_AUDIO:
                return 'AUDIO'

        #FIREWIRE
        if (node['pci.device_class'] == PCI_BASE_CLASS_SERIAL 
                and node['pci.device_subclass'] == PCI_CLASS_SERIAL_FIREWIRE):
            return 'FIREWIRE'
        #SOCKET -- PCMCIA yenta socket stuff
        if (node['pci.device_class'] == PCI_BASE_CLASS_BRIDGE 
                and (node['pci.device_subclass'] == PCI_CLASS_BRIDGE_PCMCIA
                or node['pci.device_subclass'] == PCI_CLASS_BRIDGE_CARDBUS)):
            return 'SOCKET'
    
    if node.has_key('storage.drive_type'):
        #CDROM
        if node['storage.drive_type'] == 'cdrom':
            return 'CDROM'
        #HD
        if node['storage.drive_type'] == 'disk':
            return 'HD'
         #FLOPPY
        if node['storage.drive_type'] == 'floppy':
            return 'FLOPPY'
        #TAPE
        if node['storage.drive_type'] == 'tape':
            return 'TAPE'

    #PRINTER
    if node.has_key('printer.product'):
        return 'PRINTER'

    #Catchall for specific devices, only do this after all the others
    if (node.has_key('pci.product_id') or
            node.has_key('usb.product_id')):
        return 'OTHER'

    # No class found
    return None
    
# This has got to be one of the ugliest fucntions alive
def read_cpuinfo():
    def get_entry(a, entry):
        e = entry.lower()
        if not a.has_key(e):
            return ""
        return a[e]

    if not os.access("/proc/cpuinfo", os.R_OK):
        return {}

    # Okay, the kernel likes to give us the information we need in the
    # standard "C" locale.
    if locale:
        # not really needed if you don't plan on using atof()
        locale.setlocale(locale.LC_NUMERIC, "C")

    cpulist = open("/proc/cpuinfo", "r").read()
    uname = os.uname()[4].lower()
    
    # This thing should return a hwdict that has the following
    # members:
    #
    # class, desc (required to identify the hardware device)
    # count, type, model, model_number, model_ver, model_rev
    # bogomips, platform, speed, cache
    hwdict = { 'class': "CPU",
               "desc" : "Processor",
               }
    if uname[0] == "i" and uname[-2:] == "86" or (uname == "x86_64"):
        # IA32 compatible enough
        count = 0
        tmpdict = {}
        for cpu in cpulist.split("\n\n"):
            if not len(cpu):
                continue
            count = count + 1
            if count > 1:
                continue # just count the rest
            for cpu_attr in cpu.split("\n"):
                if not len(cpu_attr):
                    continue
                vals = cpu_attr.split(':')
                if len(vals) != 2:
                    # XXX: make at least some effort to recover this data...
                    continue
                name, value = vals[0].strip(), vals[1].strip()
                tmpdict[name.lower()] = value

        if uname == "x86_64":
            hwdict['platform'] = 'x86_64'
        else:
            hwdict['platform']      = "i386"
            
        hwdict['count']         = count
        hwdict['type']          = get_entry(tmpdict, 'vendor_id')
        hwdict['model']         = get_entry(tmpdict, 'model name')
        hwdict['model_number']  = get_entry(tmpdict, 'cpu family')
        hwdict['model_ver']     = get_entry(tmpdict, 'model')
        hwdict['model_rev']     = get_entry(tmpdict, 'stepping')
        hwdict['cache']         = get_entry(tmpdict, 'cache size')
        hwdict['bogomips']      = get_entry(tmpdict, 'bogomips')
        hwdict['other']         = get_entry(tmpdict, 'flags')
        mhz_speed               = get_entry(tmpdict, 'cpu mhz')
        if mhz_speed == "":
            # damn, some machines don't report this
            mhz_speed = "-1"
        try:
            hwdict['speed']         = int(round(float(mhz_speed)) - 1)
        except ValueError:
            hwdict['speed'] = -1


    elif uname in["alpha", "alphaev6"]:
        # Treat it as an an Alpha
        tmpdict = {}
        for cpu_attr in cpulist.split("\n"):
            if not len(cpu_attr):
                continue
            vals = cpu_attr.split(':')
            if len(vals) != 2:
                # XXX: make at least some effort to recover this data...
                continue
            name, value = vals[0].strip(), vals[1].strip()
            tmpdict[name.lower()] = value.lower()

        hwdict['platform']      = "alpha"
        hwdict['count']         = get_entry(tmpdict, 'cpus detected')
        hwdict['type']          = get_entry(tmpdict, 'cpu')
        hwdict['model']         = get_entry(tmpdict, 'cpu model')
        hwdict['model_number']  = get_entry(tmpdict, 'cpu variation')
        hwdict['model_version'] = "%s/%s" % (get_entry(tmpdict, 'system type'),
                                             get_entry(tmpdict,'system variation'))
        hwdict['model_rev']     = get_entry(tmpdict, 'cpu revision')
        hwdict['cache']         = "" # pitty the kernel doesn't tell us this.
        hwdict['bogomips']      = get_entry(tmpdict, 'bogomips')
        hwdict['other']         = get_entry(tmpdict, 'platform string')
        hz_speed                = get_entry(tmpdict, 'cycle frequency [Hz]')
        # some funky alphas actually report in the form "462375000 est."
        hz_speed = hz_speed.split()
        try:
            hwdict['speed']         = int(round(float(hz_speed[0]))) / 1000000
        except ValueError:
            hwdict['speed'] = -1

    elif uname in ["ia64"]:
        tmpdict = {}
        count = 0
        for cpu in cpulist.split("\n\n"):
            if not len(cpu):
                continue
            count = count + 1
            # count the rest
            if count > 1:
                continue
            for cpu_attr in cpu.split("\n"):
                if not len(cpu_attr):
                    continue
                vals = cpu_attr.split(":")
                if len(vals) != 2:
                    # XXX: make at least some effort to recover this data...
                    continue
                name, value = vals[0].strip(), vals[1].strip()
                tmpdict[name.lower()] = value.lower()

        hwdict['platform']      = uname
        hwdict['count']         = count
        hwdict['type']          = get_entry(tmpdict, 'vendor')
        hwdict['model']         = get_entry(tmpdict, 'family')
        hwdict['model_ver']     = get_entry(tmpdict, 'archrev')
        hwdict['model_rev']     = get_entry(tmpdict, 'revision')
        hwdict['bogomips']      = get_entry(tmpdict, 'bogomips')
        mhz_speed = tmpdict['cpu mhz']
        try:
            hwdict['speed'] = int(round(float(mhz_speed)) - 1)
        except ValueError:
            hwdict['speed'] = -1
        hwdict['other']         = get_entry(tmpdict, 'features')

    elif uname in ['ppc64','ppc']:
        tmpdict = {}
        count = 0
        for cpu in cpulist.split("\n\n"):
            if not len(cpu):
                continue
            count = count + 1
            # count the rest
            if count > 1:
                continue
            for cpu_attr in cpu.split("\n"):
                if not len(cpu_attr):
                    continue
                vals = cpu_attr.split(":")
                if len(vals) != 2:
                    # XXX: make at least some effort to recover this data...
                    continue
                name, value = vals[0].strip(), vals[1].strip()
                tmpdict[name.lower()] = value.lower()

        hwdict['platform'] = uname
        hwdict['count'] = count
        hwdict['model'] = get_entry(tmpdict, "cpu")
        hwdict['model_ver'] = get_entry(tmpdict, 'revision')
        hwdict['bogomips'] = get_entry(tmpdict, 'bogomips')
        hwdict['vendor'] = get_entry(tmpdict, 'machine')
        hwdict['type'] = get_entry(tmpdict, 'platform')
        hwdict['system'] = get_entry(tmpdict, 'detected as')
        # strings are postpended with "mhz"
        mhz_speed = get_entry(tmpdict, 'clock')[:-3]
        try:
            hwdict['speed'] = int(round(float(mhz_speed)) - 1)
        except ValueError:
            hwdict['speed'] = -1
       
    elif uname in ["sparc64","sparc"]:
        tmpdict = {}
        bogomips = 0
        for cpu in cpulist.split("\n\n"):
            if not len(cpu):
                continue

            for cpu_attr in cpu.split("\n"):
                if not len(cpu_attr):
                    continue
                vals = cpu_attr.split(":")
                if len(vals) != 2:
                    # XXX: make at least some effort to recover this data...
                    continue
                name, value = vals[0].strip(), vals[1].strip()
                if name.endswith('Bogo'): 
                    if bogomips == 0:
                         bogomips = int(round(float(value)) )
                         continue
                    continue
                tmpdict[name.lower()] = value.lower()
        system = ''
        if not os.access("/proc/openprom/banner-name", os.R_OK):
            system = 'Unknown'
        if os.access("/proc/openprom/banner-name", os.R_OK):
            system = open("/proc/openprom/banner-name", "r").read() 
        hwdict['platform'] = uname
        hwdict['count'] = get_entry(tmpdict, 'ncpus probed')
        hwdict['model'] = get_entry(tmpdict, 'cpu')
        hwdict['type'] = get_entry(tmpdict, 'type')
        hwdict['model_ver'] = get_entry(tmpdict, 'type')
        hwdict['bogomips'] = bogomips
        hwdict['vendor'] = 'sun'
        hwdict['cache'] = "" # pitty the kernel doesn't tell us this.
        speed = int(round(float(bogomips))) / 2
        hwdict['speed'] = speed
        hwdict['system'] = system
         
    else:
        # XXX: expand me. Be nice to others
        hwdict['platform']      = uname
        hwdict['count']         = 1 # Good as any
        hwdict['type']          = uname
        hwdict['model']         = uname
        hwdict['model_number']  = ""
        hwdict['model_ver']     = ""
        hwdict['model_rev']     = ""
        hwdict['cache']         = ""
        hwdict['bogomips']      = ""
        hwdict['other']         = ""
        hwdict['speed']         = 0

    # make sure we get the right number here
    if not hwdict["count"]:
        hwdict["count"] = 1
    else:
        try:
            hwdict["count"] = int(hwdict["count"])
        except:
            hwdict["count"] = 1
        else:
            if hwdict["count"] == 0: # we have at least one
                hwdict["count"] = 1

    # This whole things hurts a lot.
    return hwdict



def read_memory():
    un = os.uname()
    kernel = un[2]
    if kernel[:3] == "2.6":
        return read_memory_2_6()
    if kernel[:3] == "2.4":
        return read_memory_2_4()

def read_memory_2_4():
    if not os.access("/proc/meminfo", os.R_OK):
        return {}

    meminfo = open("/proc/meminfo", "r").read()
    lines = meminfo.split("\n")
    curline = lines[1]
    memlist = curline.split()
    memdict = {}
    memdict['class'] = "MEMORY"
    megs = int(long(memlist[1])/(1024*1024))
    if megs < 32:
        megs = megs + (4 - (megs % 4))
    else:
        megs = megs + (16 - (megs % 16))
    memdict['ram'] = str(megs)
    curline = lines[2]
    memlist = curline.split()
    # otherwise, it breaks on > ~4gigs of swap
    megs = int(long(memlist[1])/(1024*1024))
    memdict['swap'] = str(megs)
    return memdict

def read_memory_2_6():
    if not os.access("/proc/meminfo", os.R_OK):
        return {}
    meminfo = open("/proc/meminfo", "r").read()
    lines = meminfo.split("\n")
    dict = {}
    for line in lines:
        blobs = line.split(":", 1)
        key = blobs[0]
        if len(blobs) == 1:
            continue
        #print blobs
        value = blobs[1].strip()
        dict[key] = value

    memdict = {}
    memdict["class"] = "MEMORY"

    total_str = dict['MemTotal']
    blips = total_str.split(" ")
    total_k = long(blips[0])
    megs = long(total_k/(1024))

    swap_str = dict['SwapTotal']
    blips = swap_str.split(' ')
    swap_k = long(blips[0])
    swap_megs = long(swap_k/(1024))

    memdict['ram'] = str(megs)
    memdict['swap'] = str(swap_megs)
    return memdict

def getUUID():
    try:
        UUID = file('/etc/sysconfig/hw-uuid').read().strip()
    except IOError:
        try:
            UUID = file('/proc/sys/kernel/random/uuid').read().strip()
            try:
                file('/etc/sysconfig/hw-uuid', 'w').write(self.UUID)
            except:
                sys.stderr.write('Unable to save UUID, continuing...\n')
        except IOError:
            sys.stderr.write('Unable to determine UUID of system!\n')
            sys.exit(1)
    return UUID