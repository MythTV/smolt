#
# Copyright (c) 1999-2002 Red Hat, Inc.  Distributed under GPL.
#
# Author: Preston Brown <pbrown@redhat.com>
#         Adrian Likins <alikins@redhat.com>
#         Cristian Gafton <gafton@redhat.com>
#
# This thing gets the hardware configuraion out of a system
"""Used to read hardware info from kudzu, /proc, etc"""
from socket import gethostname
from socket import gethostbyname
import socket

import os
import sys
import string
import types

import config

from rhpl import ethtool
from rhpl.translate import _, N_
from haltree import HalTree, HalDevice

import dbus

#PCI DEVICE DEFINES
# These are taken from pci_ids.h in the linux kernel source and used to 
# properly identify the hardware
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



# Some systems don't have the _locale module installed
try:
    import locale
except ImportError:
    locale = None


# read_hal()
# 
# This reads in all the properties for each device from HAL, storing the 
# property names & values into a dict.  A list of dicts is returned.
#
# This only works on newer versions of dbus & HAL (as found in RHEL5)
def read_hal():
    ret = []
    bus = dbus.SystemBus()
        
    hal_manager_obj = bus.get_object('org.freedesktop.Hal',
        '/org/freedesktop/Hal/Manager')
    hal_manager = dbus.Interface(hal_manager_obj,
        'org.freedesktop.Hal.Manager')
   
    device_list = hal_manager.GetAllDevices()
    hal_tree = HalTree()
    for udi in device_list:
        device_obj = bus.get_object ('org.freedesktop.Hal', udi)
        device = dbus.Interface(device_obj, 'org.freedesktop.Hal.Device')

        properties = device.GetAllProperties()

        haldev = HalDevice(properties)
        hal_tree.add(haldev)

    kudzu_list = process_hal_nodes(hal_tree.head)
    return kudzu_list
    
    # Recursive function, does all the dirty work for add_hal_hardware
def process_hal_nodes(node):
    kudzu_list = []
    node.classification = classify_hal(node)
    if node.classification:
        parent = node.parent
        dev = {} 
        dev['class'] = node.classification
        #get bus
        dev['bus'] = get_device_bus(node)
        
        #get scsi info
        if dev['bus'] == 'scsi':
            if parent.properties.has_key('scsi.host'):
                dev['prop1'] = parent.properties['scsi.host']
            if parent.properties.has_key('scsi.target'):
                dev['prop2'] = parent.properties['scsi.target']
            if parent.properties.has_key('scsi.bus'):
                dev['prop3'] = parent.properties['scsi.bus']
            if parent.properties.has_key('scsi.lun'):
                dev['prop4'] = parent.properties['scsi.lun']
        
        
        dev['driver'] = get_device_driver(node) 
        
        device_path = get_device_path(node)
        if device_path:
            dev['device'] = device_path

        dev['desc'] = get_device_description(node)

        dev['pciType'] = get_device_pcitype(node)

        dev['detached'] = 0
        kudzu_list.append(dev)

    for child in node.children:
        child_list = process_hal_nodes(child) 
        kudzu_list.extend(child_list)

    return kudzu_list
        
        

def classify_hal(node):
    # NETWORK
    if node.properties.has_key('net.interface'):
        return 'NETWORK'
    
    if node.properties.has_key('info.product') and node.properties.has_key('info.category'):
        if node.properties['info.category'] == 'input':
            # KEYBOARD <-- do this before mouse, some keyboards have built-in mice
            if 'keyboard' in node.properties['info.product'].lower():
                return 'KEYBOARD'
            # MOUSE
            if 'mouse' in node.properties['info.product'].lower():
                return 'MOUSE'
    
    if node.properties.has_key('pci.device_class'):
        #VIDEO
        if node.properties['pci.device_class'] == PCI_BASE_CLASS_DISPLAY:
            return 'VIDEO'
        #USB
        if (node.properties['pci.device_class'] ==  PCI_BASE_CLASS_SERIAL
                and node.properties['pci.device_subclass'] == PCI_CLASS_SERIAL_USB):
            return 'USB'
        
        if node.properties['pci.device_class'] == PCI_BASE_CLASS_STORAGE: 
            #IDE
            if node.properties['pci.device_subclass'] == PCI_CLASS_STORAGE_IDE:
                return 'IDE'
            #SCSI
            if node.properties['pci.device_subclass'] == PCI_CLASS_STORAGE_SCSI:
                return 'SCSI'
            #RAID
            if node.properties['pci.device_subclass'] == PCI_CLASS_STORAGE_RAID:
                return 'RAID'
        #MODEM
        if (node.properties['pci.device_class'] == PCI_BASE_CLASS_COMMUNICATION 
                and node.properties['pci.device_subclass'] == PCI_CLASS_COMMUNICATION_MODEM):
            return 'MODEM'
        #SCANNER 
        if (node.properties['pci.device_class'] == PCI_BASE_CLASS_INPUT 
                and node.properties['pci.device_subclass'] == PCI_CLASS_INPUT_SCANNER):
            return 'SCANNER'
        
        if node.properties['pci.device_class'] == PCI_BASE_CLASS_MULTIMEDIA: 
            #CAPTURE -- video capture card
            if node.properties['pci.device_subclass'] == PCI_CLASS_MULTIMEDIA_VIDEO:
                return 'CAPTURE'
            #AUDIO
            if node.properties['pci.device_subclass'] == PCI_CLASS_MULTIMEDIA_AUDIO:
                return 'AUDIO'

        #FIREWIRE
        if (node.properties['pci.device_class'] == PCI_BASE_CLASS_SERIAL 
                and node.properties['pci.device_subclass'] == PCI_CLASS_SERIAL_FIREWIRE):
            return 'FIREWIRE'
        #SOCKET -- PCMCIA yenta socket stuff
        if (node.properties['pci.device_class'] == PCI_BASE_CLASS_BRIDGE 
                and (node.properties['pci.device_subclass'] == PCI_CLASS_BRIDGE_PCMCIA
                or node.properties['pci.device_subclass'] == PCI_CLASS_BRIDGE_CARDBUS)):
            return 'SOCKET'
    
    if node.properties.has_key('storage.drive_type'):
        #CDROM
        if node.properties['storage.drive_type'] == 'cdrom':
            return 'CDROM'
        #HD
        if node.properties['storage.drive_type'] == 'disk':
            return 'HD'
         #FLOPPY
        if node.properties['storage.drive_type'] == 'floppy':
            return 'FLOPPY'
        #TAPE
        if node.properties['storage.drive_type'] == 'tape':
            return 'TAPE'

    #PRINTER
    if node.properties.has_key('printer.product'):
        return 'PRINTER'

    #Catchall for specific devices, only do this after all the others
    if (node.properties.has_key('pci.product_id') or
            node.properties.has_key('usb.product_id')):
        return 'OTHER'

    # No class found
    return None

def get_device_bus(node):
    if node.properties.has_key('storage.bus'):
        bus = node.properties['storage.bus']
    elif node.properties.has_key('info.bus'):
        if node.properties['info.bus'] == 'platform':
            bus = 'MISC'
        else:
            bus = node.properties['info.bus']
    else:
        bus = 'MISC'
    
    return bus

def get_device_driver(node):
    if node.properties.has_key('info.linux.driver'):
        driver = node.properties['info.linux.driver']
    elif node.properties.has_key('net.linux.driver'):
        driver = node.properties['net.linux.driver']
    else:
        driver = 'unknown'

    return driver

def get_device_path(node):
    """
    Return the device file path.

    As kudzu did not return a string with the /dev/ prefix,
    this function will not, either.
    RHN's DB has a limit of 16 characters for the device path.
    If the path is longer than that, return None.
    If no device path is found, return None.
    """
    dev = None

    if node.properties.has_key('block.device'):
        dev = node.properties['block.device']
    elif node.properties.has_key('linux.device_file'):
        dev = node.properties['linux.device_file']
    elif (node.classification == 'NETWORK' 
            and node.properties.has_key('net.interface')):
        dev = node.properties['net.interface']

    if dev:
        if dev.startswith('/dev/'):
            dev = dev[5:]
        if len(dev) > 16:
            dev = None

    return dev

def get_device_description(node):
    if (node.properties.has_key('info.vendor') 
            and node.properties.has_key('info.product')):
        desc = node.properties['info.vendor'] + '|' +  node.properties['info.product']
    elif (node.properties.has_key('info.vendor')):
        desc = node.properties['info.vendor'] 
    elif node.properties.has_key('info.product'):
        desc =  node.properties['info.product']
    else:
        desc = ""
    
    return desc

def get_device_pcitype(node):
    PCI_TYPE_PCMCIA = 2
    PCI_TYPE_PCI = 1
    PCI_TYPE_NOT_PCI = -1
    
    if (node.properties.has_key('info.bus') 
            and node.properties['info.bus'] == 'pci'):
        parent = node.parent
        if (parent.properties.has_key('pci.device_class') 
                and (parent.properties['pci.device_class'] == 6 
                and (parent.properties['pci.device_subclass'] == 5 
                or parent.properties['pci.device_subclass'] == 7))):
            pcitype = PCI_TYPE_PCMCIA
        else:
            pcitype = PCI_TYPE_PCI
    else:
        pcitype = PCI_TYPE_NOT_PCI

    return pcitype

def read_installinfo():
    if not os.access("/etc/sysconfig/installinfo", os.R_OK):
        return {}
    installinfo = open("/etc/sysconfig/installinfo", "r").readlines()
    installdict = {}
    installdict['class'] = "INSTALLINFO"
    for info in installinfo:
        if not len(info):
            continue
        vals = string.split(info, '=')
        if len(vals) <= 1:
            continue
        strippedstring = string.strip(vals[0])
        vals[0] = strippedstring
        
        installdict[vals[0]] = string.strip(string.join(vals[1:]))
    return installdict
    
        

# This has got to be one of the ugliest fucntions alive
def read_cpuinfo():
    def get_entry(a, entry):
        e = string.lower(entry)
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
    uname = string.lower(os.uname()[4])

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
        for cpu in string.split(cpulist, "\n\n"):
            if not len(cpu):
                continue
            count = count + 1
            if count > 1:
                continue # just count the rest
            for cpu_attr in string.split(cpu, "\n"):
                if not len(cpu_attr):
                    continue
                vals = string.split(cpu_attr, ":")
                if len(vals) != 2:
                    # XXX: make at least some effort to recover this data...
                    continue
                name, value = string.strip(vals[0]), string.strip(vals[1])
                tmpdict[string.lower(name)] = value

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
        for cpu_attr in string.split(cpulist, "\n"):
            if not len(cpu_attr):
                continue
            vals = string.split(cpu_attr, ":")
            if len(vals) != 2:
                # XXX: make at least some effort to recover this data...
                continue
            name, value = string.strip(vals[0]), string.strip(vals[1])
            tmpdict[string.lower(name)] = string.lower(value)

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
        hz_speed = string.split(hz_speed)
        try:
            hwdict['speed']         = int(round(float(hz_speed[0]))) / 1000000
        except ValueError:
            hwdict['speed'] = -1

    elif uname in ["ia64"]:
        tmpdict = {}
        count = 0
        for cpu in string.split(cpulist, "\n\n"):
            if not len(cpu):
                continue
            count = count + 1
            # count the rest
            if count > 1:
                continue
            for cpu_attr in string.split(cpu, "\n"):
                if not len(cpu_attr):
                    continue
                vals = string.split(cpu_attr, ":")  
                if len(vals) != 2:
                    # XXX: make at least some effort to recover this data...
                    continue
                name, value = string.strip(vals[0]), string.strip(vals[1])
                tmpdict[string.lower(name)] = string.lower(value)

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
        for cpu in string.split(cpulist, "\n\n"):
            if not len(cpu):
                continue
            count = count + 1
            # count the rest
            if count > 1:
                continue
            for cpu_attr in string.split(cpu, "\n"):
                if not len(cpu_attr):
                    continue
                vals = string.split(cpu_attr, ":")  
                if len(vals) != 2:
                    # XXX: make at least some effort to recover this data...
                    continue
                name, value = string.strip(vals[0]), string.strip(vals[1])
                tmpdict[string.lower(name)] = string.lower(value)

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
        for cpu in string.split(cpulist, "\n\n"):
            if not len(cpu):
                continue

            for cpu_attr in string.split(cpu, "\n"):
                if not len(cpu_attr):
                    continue
                vals = string.split(cpu_attr, ":")
                if len(vals) != 2:
                    # XXX: make at least some effort to recover this data...
                    continue
                name, value = string.strip(vals[0]), string.strip(vals[1])
                if name.endswith('Bogo'): 
                    if bogomips == 0:
                         bogomips = int(round(float(value)) )
                         continue
                    continue
                tmpdict[string.lower(name)] = string.lower(value)
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
    lines = string.split(meminfo,"\n")
    curline = lines[1]
    memlist = string.split(curline)
    memdict = {}
    memdict['class'] = "MEMORY"
    megs = int(long(memlist[1])/(1024*1024))
    if megs < 32:
        megs = megs + (4 - (megs % 4))
    else:
        megs = megs + (16 - (megs % 16))
    memdict['ram'] = str(megs)
    curline = lines[2]
    memlist = string.split(curline)
    # otherwise, it breaks on > ~4gigs of swap
    megs = int(long(memlist[1])/(1024*1024))
    memdict['swap'] = str(megs)
    return memdict

def read_memory_2_6():
    if not os.access("/proc/meminfo", os.R_OK):
        return {}
    meminfo = open("/proc/meminfo", "r").read()
    lines = string.split(meminfo,"\n")
    dict = {}
    for line in lines:
        blobs = string.split(line, ":", 1)
        key = blobs[0]
        if len(blobs) == 1:
            continue
        #print blobs
        value = string.strip(blobs[1])
        dict[key] = value
        
    memdict = {}
    memdict["class"] = "MEMORY"
    
    total_str = dict['MemTotal']
    blips = string.split(total_str, " ")
    total_k = long(blips[0])
    megs = long(total_k/(1024))

    swap_str = dict['SwapTotal']
    blips = string.split(swap_str, ' ')
    swap_k = long(blips[0])
    swap_megs = long(swap_k/(1024))

    memdict['ram'] = str(megs)
    memdict['swap'] = str(swap_megs)
    return memdict


def findHostByRoute():
    cfg = config.initUp2dateConfig()
    sl = cfg['serverURL']
    if type(sl) == type(""):
        sl  = [sl]

    st = {'https':443, 'http':80}
    hostname = None
    intf = None
    for serverUrl in sl:
        s = socket.socket()
        server = string.split(serverUrl, '/')[2]
        servertype = string.split(serverUrl, ':')[0]
        port = st[servertype]
        
        if cfg['enableProxy']:
            server_port = config.getProxySetting()
            (server, port) = string.split(server_port, ':')
            port = int(port)

        try:
            # RHEL3 doesn't let you set a timeout, see #164660
            if hasattr(s, "settimeout"):
                s.settimeout(5)
            s.connect((server, port))
            (intf, port) = s.getsockname()
            hostname = socket.gethostbyaddr(intf)[0]
        # I dislike generic excepts, but is the above fails
        # for any reason, were not going to be able to
        # find a good hostname....
        except:
            s.close()
            continue
    if hostname == None:
        hostname = "unknown"
        s.close()
    return hostname, intf
    
def read_network():
    netdict = {}
    netdict['class'] = "NETINFO"

    netdict['hostname'] = gethostname()
    try:
        netdict['ipaddr'] = gethostbyname(gethostname())
    except:
        netdict['ipaddr'] = "127.0.0.1"


    if netdict['hostname'] == 'localhost.localdomain' or \
    netdict['ipaddr'] == "127.0.0.1":
        hostname, ipaddr = findHostByRoute()
        netdict['hostname'] = hostname
        netdict['ipaddr'] = ipaddr

    return netdict

def read_network_interfaces():
    intDict = {}
    intDict['class'] = "NETINTERFACES"
    
    interfaces = ethtool.get_devices()
    for interface in interfaces:
        try:
            hwaddr = ethtool.get_hwaddr(interface)
        except:
            hwaddr = ""
            
        try:
            module = ethtool.get_module(interface)
        except:
            if interface == 'lo':
                module = "loopback"
            else:
                module = "Unknown"
        try:
            ipaddr = ethtool.get_ipaddr(interface)
        except:
            ipaddr = ""

        try:
            netmask = ethtool.get_netmask(interface)
        except:
            netmask = ""

        try:
            broadcast = ethtool.get_broadcast(interface)
        except:
            broadcast = ""
            
        intDict[interface] = {'hwaddr':hwaddr,
                              'ipaddr':ipaddr,
                              'netmask':netmask,
                              'broadcast':broadcast,
                              'module': module}

    return intDict


def get_device_property(device, property_name):
    """ Return a hal device property, or None if it does not exist. """
    if device.PropertyExists(property_name):
        # Convert from unicode to ascii in case the server can't handle it.
        return str(device.GetProperty(property_name))
    else:
        return None

def get_hal_computer():
    bus = dbus.SystemBus()
    computer_obj = bus.get_object("org.freedesktop.Hal",
        "/org/freedesktop/Hal/devices/computer")
    computer = dbus.Interface(computer_obj, "org.freedesktop.Hal.Device")

    return computer
   
# Read DMI information via hal.    
def read_dmi():
    computer = get_hal_computer()

    dmidict = {}
  
    vendor = get_device_property(computer, "system.vendor")
    if vendor:
        dmidict["vendor"] = vendor

    s = ""
    product = get_device_property(computer, "system.product")
    if product:
        s = product
    version = get_device_property(computer, "smbios.system.version")
    if version:
        s = s + " " + version
    if s:
        dmidict["system"] = s
   
    product = get_device_property(computer, "smbios.board.product")
    if product:
        dmidict["product"] = product
    vendor = get_device_property(computer, "smbios.board.vendor")
    if vendor:
        dmidict["board"] = vendor

    vendor = get_device_property(computer, "smbios.bios.vendor")
    if vendor:
        dmidict["bios_vendor"] = vendor
    version = get_device_property(computer, "smbios.bios.version")
    if version:
        dmidict["bios_version"] = version
    release = get_device_property(computer, "smbios.bios.release")
    if release:
        dmidict["bios_release"] = release

    # The hairy part is figuring out if there is an asset tag/serial number of importance
    asset = ""
    for k in ["chassis", "board", "system"]:
        for l in ["serial", "asset"]:
            asset_value = get_device_property(computer, "smbios." + k + "." + l)
            if not asset_value:
                continue
            t = string.strip(asset_value)
            if t in [None, "", "Not Available", "None", "N/A"]:
                continue
            asset = "%s(%s: %s) " % (asset, k, t)
    if asset:
        dmidict["asset"] = asset
    # Clean up empty entries    
    for k in dmidict.keys()[:]:
        if dmidict[k] is None:
            del dmidict[k]
    # Finished
    dmidict["class"] = "DMI"
    
    return dmidict

def get_hal_system_and_smbios():
    computer = get_hal_computer()

    props = computer.GetAllProperties()
    
    system_and_smbios = {}

    for key in props:
        if key.startswith('system') or key.startswith('smbios'):
            system_and_smbios[key] = props[key]

    return system_and_smbios

# this one reads it all
def Hardware():
    allhw = []

    try:
        ret = read_hal()
        if ret: 
            allhw = ret
    except:
        print _("Error reading hardware information:"), sys.exc_type
    # all others return individual arrays

    # cpu info
    try:
        ret = read_cpuinfo()
        if ret: allhw.append(ret)
    except:
        print _("Error reading cpu information:"), sys.exc_type
        
    # memory size info
    try:
        ret = read_memory()
        if ret: allhw.append(ret)
    except:
        print _("Error reading system memory information:"), sys.exc_type
        
    # minimal networking info
    try:
        ret = read_network()
        if ret: 
            allhw.append(ret)
    except:
        print _("Error reading networking information:"), sys.exc_type
    # dont like catchall exceptions but theres not
    # really anything useful we could do at this point
    # and its been trouble prone enough 

    # minimal DMI info
    try:
        ret = read_dmi()
        if ret:
            allhw.append(ret)
    except:
        print _("Error reading DMI information:"), sys.exc_type

    try:
        ret = read_installinfo()
        if ret:
            allhw.append(ret)
    except:
        print _("Error reading install method information:"), sys.exc_type

    try:
        ret = read_network_interfaces()
        if ret:
            allhw.append(ret)
    except:
        print _("Error reading network interface information:"), sys.exc_type
    # all Done.
    return allhw

# XXX: Need more functions here:
#  - filesystems layout (/proc.mounts and /proc/mdstat)
#  - is the kudzu config enough or should we strat chasing lscpi and try to parse that
#    piece of crap output?

#
# Main program
#
if __name__ == '__main__':
    for hw in Hardware():
        for k in hw.keys():
            print "'%s' : '%s'" % (k, hw[k])
        print
