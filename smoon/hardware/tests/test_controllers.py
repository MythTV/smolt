import turbogears
from turbogears import testutil, database
import logging
import cherrypy
import simplejson

from hardware.model import *
from hardware import model
from hardware.controllers import Root


turbogears.update_config(configfile='../test.cfg', modulename='hardware.config')

cherrypy.root = Root()
root = cherrypy.root

def test_add_old():
    "testing to make sure an add via the 0.91 protocol completes"
    UUID = "sheep!"
    OS = "Wintendo"
    platform = "Super Mario"
    bogomips = 2
    systemMemory = 640
    systemSwap = 640
    CPUVendor = "Death"
    CPUModel = "F00F"
    numCPUs = 0
    CPUSpeed = 0
    language = "Newspeak"
    defaultRunlevel = 6
    vendor = "eMachines"
    system = "reboot O'Matic"
    lsbRelease = "OOXML"
    formfactor = "Sparta!"
    kernelVersion = "NT"
    selinux_enabled = False
    selinux_policy = "Security?"
    smoltProtocol = ".91"
    
    token_result = testutil.call(root.token, uuid = UUID)
    assert token_result["prefered_protocol"] == ".91"
    token =  token_result['token']
    
    add_result = testutil.call(root.add, uuid = UUID, OS = OS, \
                               platform = platform, \
                               bogomips = bogomips, \
                               systemMemory = systemMemory, \
                               systemSwap = systemSwap, \
                               CPUVendor = CPUVendor, \
                               CPUModel = CPUModel, \
                               numCPUs = numCPUs, \
                               CPUSpeed = CPUSpeed, \
                               language = language, \
                               defaultRunlevel = defaultRunlevel, \
                               vendor = vendor, \
                               system = system, \
                               token = token, \
                               lsbRelease = lsbRelease, \
                               formfactor = formfactor, \
                               kernelVersion = kernelVersion, \
                               selinux_enabled = selinux_enabled, \
                               selinux_policy = selinux_policy, \
                               smoltProtocol = smoltProtocol)
    
    test_host = Query(Host).selectone_by(uuid=UUID)
    assert test_host.uuid == UUID
    assert test_host.os == OS
    assert test_host.platform == platform
    assert test_host.cpu_model == CPUModel
    assert test_host.num_cpus == numCPUs
    assert test_host.cpu_speed == CPUSpeed
    assert test_host.language == language
    assert test_host.default_runlevel == defaultRunlevel
    assert test_host.vendor == vendor
    assert test_host.system == system
    assert test_host.formfactor == formfactor
    assert test_host.kernel_version == kernelVersion
    assert test_host.selinux_enabled == selinux_enabled
    assert test_host.selinux_policy == selinux_policy
    
    vendor_id = 42
    device_id = 42
    subsys_vendor_id = 43
    subsys_device_id = 44
    bus = "the short one"
    driver = "santaclause"
    cls = "HEGEMONIC"
    description = '"It\'s hot enough to boil a monkey\'s bum!", the Prime Minister said, and her majesty smiled to herself'
    #She's a good sheila, and not at all stuckup
    device = "%s|%s|%s|%s|%s|%s|%s|%s" % (vendor_id,
                                          device_id,
                                          subsys_vendor_id,
                                          subsys_device_id,
                                          bus,
                                          driver,
                                          cls,
                                          description)
    device = "%s\n%s" % (device, device)
    addDevice_result = testutil.call(root.addDevices, uuid=UUID, Devices=device)
    
    test_device = Query(ComputerLogicalDevice).selectone_by(description=description)
    
    assert test_device.description == description
    assert test_device.vendor_id == vendor_id
    assert test_device.device_id == device_id
    assert test_device.subsys_vendor_id == subsys_vendor_id
    assert test_device.subsys_device_id == subsys_device_id
    assert test_device.bus == bus
    assert test_device.driver == driver
    assert test_device.hardware_class.cls == cls
    
    test_host_link = Query(HostLink).select_by(device_id=test_device.id)[0]
    
    assert test_host_link.device_id == test_device.id
    assert test_host_link.host_link_id == test_host.id
    
#    session.delete(test_host)
#    session.delete(test_device)
    session.flush()

def test_add_new():
    """Testing to make sure an add with the new protocol works"""
    smoltProtocol = "0.97"
    UUID = "sheep!"
    OS = "Wintendo"
    platform = "Super Mario"
    bogomips = 2
    systemMemory = 640
    systemSwap = 640
    CPUVendor = "Death"
    CPUModel = "F00F"
    numCPUs = 0
    CPUSpeed = 0
    language = "Newspeak"
    defaultRunlevel = 6
    vendor = "eMachines"
    system = "reboot O'Matic"
    lsbRelease = "OOXML"
    formfactor = "skinny"
    kernelVersion = "NT"
    selinux_enabled = False
    selinux_policy = "Security?"
    vendor_id = 42
    device_id = 42
    subsys_vendor_id = 43
    subsys_device_id = 44
    bus = "the short one"
    driver = "santaclause"
    cls = "HEGEMONIC"
    description = '"It\'s hot enough to boil a monkey\'s bum!", the Prime Minister said, and her majesty smiled to herself'
    #She's a good sheila, and not at all stuckup
    
    host = {'uuid' :            "sheep!",
            'os' :              "Wintendo",
            'default_runlevel': 6,
            'language' :        "Newspeak",
            'platform' :        "Super Mario",
            'bogomips' :        2,
            'cpu_vendor' :      "Death",
            'cpu_model' :       "F00F",
            'num_cpus':         0,
            'cpu_speed' :       0,
            'system_memory' :   640,
            'system_swap' :     640,
            'vendor' :          "eMachines",
            'system' :          "reboot O'Matic",
            'kernel_version' :  "NT",
            'formfactor' :      "skinny",
            'selinux_enabled':  False,
            'selinux_policy':  "Security?"}
    device = [{"vendor_id": 42,
               "device_id": 42,
               "subsys_vendor_id": 43,
               "subsys_device_id": 44,
               "bus": "the short one",
               "driver": "santaclause",
               "type": "HEGEMONIC",
               "description": '"It\'s hot enough to boil a monkey\'s bum!", the Prime Minister said, and her majesty smiled to herself'}]
    #She's a good sheila, and not at all stuckup
    host["devices"] = device
    host['smolt_protocol'] = smoltProtocol
    host_json = simplejson.dumps(host)
    

    
    token_result = testutil.call(root.token_json, uuid = UUID)
    assert token_result["prefered_protocol"] == "0.97"
    token =  token_result['token']
    
    add_result = testutil.call(root.add_json, uuid=host['uuid'],
                               smolt_protocol=smoltProtocol,
                               token=token, host=host_json)
    
    test_host = Query(Host).selectone_by(uuid=UUID)
    assert test_host.uuid == UUID
    assert test_host.os == OS
    assert test_host.platform == platform
    assert test_host.cpu_model == CPUModel
    assert test_host.num_cpus == numCPUs
    assert test_host.cpu_speed == CPUSpeed
    assert test_host.language == language
    assert test_host.default_runlevel == defaultRunlevel
    assert test_host.vendor == vendor
    assert test_host.system == system
    assert test_host.formfactor == formfactor
    assert test_host.kernel_version == kernelVersion
    assert test_host.selinux_enabled == selinux_enabled
    assert test_host.selinux_policy == selinux_policy
    
    test_device = Query(ComputerLogicalDevice).selectone_by(description=description)
    
    assert test_device.description == description
    assert test_device.vendor_id == vendor_id
    assert test_device.device_id == device_id
    assert test_device.subsys_vendor_id == subsys_vendor_id
    assert test_device.subsys_device_id == subsys_device_id
    assert test_device.bus == bus
    assert test_device.driver == driver
    assert test_device.hardware_class.cls == cls
    
    test_host_link = Query(HostLink).select_by(device_id=test_device.id)[0]
    
    assert test_host_link.device_id == test_device.id
    assert test_host_link.host_link_id == test_host.id
    
    print "device: %s" % test_device.host_links
    print "host: %s" % test_host.devices
    print "link: %s" % test_host_link
    
    session.delete(test_host)
    session.flush()
    session.refresh(test_device)
    print "new device: %s" % test_device
    print test_device.host_links
    print test_device.id
    print test_device.description
    session.delete(test_device)
    session.flush()
