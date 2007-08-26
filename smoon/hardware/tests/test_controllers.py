import turbogears
from turbogears import testutil, database
import logging
import cherrypy

from hardware.model import *
from hardware import model
from hardware.controllers import Root


turbogears.update_config(configfile='../test.cfg', modulename='hardware.config')

cherrypy.root = Root()
root = cherrypy.root

def test_method():
    "the index method should return a string called now"
    import types
    result = testutil.call(cherrypy.root.index)
    assert type(result["now"]) == types.StringType

def test_indextitle():
    "The mainpage should have the right title"
    testutil.createRequest("/")
    assert "Smolt" in cherrypy.response.body[0]

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
    selinux_enforce = "Security?"
    smoltProtocol = ".91"
    
    token_result = testutil.call(root.token, UUID = UUID)
    assert token_result["prefered_protocol"] == ".91"
    token =  token_result['token']
    
    add_result = testutil.call(root.add, UUID = UUID, OS = OS, \
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
                               selinux_enforce = selinux_enforce, \
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
    assert test_host.selinux_enforce == selinux_enforce
    
    vendor_id = 42
    device_id = "42"
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
    addDevice_result = testutil.call(root.addDevices, UUID=UUID, Devices=device)
    
    test_device = Query(ComputerLogicalDevice).selectone_by(description=description)
    
    assert test_device.description == description
    assert test_device.vendor_id == vendor_id
    print test_device.device_id.__class__
    print device_id.__class__
    assert test_device.device_id == device_id
    assert test_device.subsys_vendor_id == subsys_vendor_id
    assert test_device.subsys_device_id == subsys_device_id
    assert test_device.bus == bus
    assert test_device.driver == driver
    assert test_device.hardware_class.cls == cls
    
    test_host_link = Query(HostLink).select_by(device_id=test_device.id)[0]
    
    assert test_host_link.device_id == test_device.id
    print test_host_link.host_link_id
    print test_host.id
    assert test_host_link.host_link_id == test_host.id
    
    ctx.current.delete(test_host)
    ctx.current.flush()
    
    
    
