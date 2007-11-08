import urllib
import time
import datetime
import sys

from Crypto.Cipher import XOR
from cherrypy import request, response
from mx import DateTime
import simplejson
from sqlalchemy import *
from sqlalchemy.exceptions import InvalidRequestError
from turbogears import controllers, expose, identity
from turbogears import exception_handler
from turbogears import scheduler
from turbogears import redirect
from turbogears import widgets
from turbogears import flash
from turbogears.widgets import Tabber, JumpMenu
from ratingwidget import SingleRatingWidget, RatingWidget

from hardware.model import *
from hwdata import DeviceMap
from smoonexceptions import NotCachedException

import logging
log = logging.getLogger("smoon")

# This is such a bad idea, yet here it is.
CRYPTPASS = 'PleaseChangeMe11'
currentSmoltProtocol = '0.97' 

def getDeviceWikiLink(device):
    return '/wiki/%s/%04x/%04x/%04x/%04x' % (device.bus,
                                             int(device.vendor_id or 0),
                                             int(device.device_id or 0),
                                             int(device.subsys_vendor_id or 0),
                                             int(device.subsys_device_id or 0))

def getHostWikiLink(host):
    return '/wiki/System/%s/%s' % (host.vendor, host.system)

class Root(controllers.RootController):
    def __init__(self):
        controllers.RootController.__init__(self)

        
    @expose(template="hardware.templates.welcome")
    def index(self):
        import time
        # log.debug("Happy TurboGears Controller Responding For Duty")
        return dict(now=time.ctime())


    @expose(template="hardware.templates.login")
    def login(self, forward_url=None, previous_url=None, *args, **kw):

        if not identity.current.anonymous \
            and identity.was_login_attempted() \
            and not identity.get_identity_errors():
            raise redirect(forward_url)

        forward_url=None
        previous_url= request.path

        if identity.was_login_attempted():
            msg=_("The credentials you supplied were not correct or "
                   "did not grant access to this resource.")
        elif identity.get_identity_errors():
            msg=_("You must provide your credentials before accessing "
                   "this resource.")
        else:
            msg=_("Please log in.")
            forward_url= request.headers.get("Referer", "/")

        response.status=403
        return dict(message=msg, previous_url=previous_url, logging_in=True,
                    original_parameters=request.params,
                    forward_url=forward_url)


    @expose(template="hardware.templates.error")
    def error_client(self, tg_exceptions=None):
        ''' Exception handler, Sends messages back to the client'''
        message = 'ServerMessage: %s' % tg_exceptions
        return dict(handling_value=True,exception=message)

    @expose(template="hardware.templates.error")
    def error_web(self, tg_exceptions=None):
        ''' Exception handler, Sends messages back to the client'''
        message = 'Error: %s' % tg_exceptions
        return dict(handling_value=True,exception=message)

    @expose(template="hardware.templates.show")
    @exception_handler(error_web,rules="isinstance(tg_exceptions,ValueError)")
    def show(self, UUID=''):
        try:
            uuid = u'%s' % UUID.strip()
            uuid = uuid.encode('utf8')
        except:
            raise ValueError("Critical: Unicode Issue - Tell Mike!")

        try:
            host_object = Query(Host).selectone_by(uuid=UUID)
            #ctx.current.refresh(host_object)
        except:
            raise ValueError("Critical: UUID Not Found - %s" % UUID)
        devices = {}
        ven = DeviceMap('pci')

        for dev in host_object.devices:
            #ctx.current.refresh(dev)
            device = dev.device
            if not device.vendor_id and device.device_id:
                continue
            device_name = ""
            vname = ven.vendor(device.vendor_id, bus=device.bus)
            if vname and vname != "N/A":
                device_name += vname
            dname = ven.device(device.vendor_id, device.device_id, alt=device.description, bus=device.bus)
            if dname and dname != "N/A":
                device_name += " " + dname
            svname = ven.vendor(device.subsys_device_id)
            if svname and svname != "N/A":
                device_name += " " + svname
            sdname = ven.subdevice(device.vendor_id, device.device_id, device.subsys_vendor_id, device.subsys_device_id)
            if sdname and sdname != "N/A":
                device_name += " " + sdname

            #This is to prevent duplicate devices showing up, in the future,
            #There will be no dups in the database
            devices[dev.device_id] = dict(id = dev.device_id,
                                          name = device_name,
                                          link = getDeviceWikiLink(device),
                                          cls = device.cls,
                                          rating = dev.rating,
                                          )

        devices = devices.values()
        devices.sort(key=lambda x: x.get('cls'))

        return dict(host_object = host_object, 
                    host_link = getHostWikiLink(host_object),
                    devices=devices,
                    ratingwidget=SingleRatingWidget(),
                    )

        
    @expose(template="hardware.templates.showall")
    @exception_handler(error_web,rules="isinstance(tg_exceptions,ValueError)")
    def show_all(self, UUID=''):
        try:
            uuid = u'%s' % UUID.strip()
            uuid = uuid.encode('utf8')
        except:
            raise ValueError("Critical: Unicode Issue - Tell Mike!")
        try:
            host_object = Query(Host).selectone_by(uuid=UUID)
            #ctx.current.refresh(host_object)
        except:
            raise ValueError("Critical: UUID Not Found - %s" % UUID)
        devices = {}
        for dev in host_object.devices:
            #ctx.current.refresh(dev)
            #This is to prevent duplicate devices showing up, in the future,
            #There will be no dups in the database
            devices[dev.device_id] = (dev.device, dev.rating)
        ven = DeviceMap('pci')

        devices = devices.values()
        devices.sort(key=lambda x: x[0].cls)

        return dict(host_object=host_object,
                    host_link = getHostWikiLink(host_object),
                    devices=devices, ven=ven,
                    ratingwidget=SingleRatingWidget(),
                    getDeviceWikiLink = getDeviceWikiLink,
                    )

    @expose()
    def time(self):
        import time
        return time.ctime()

    @expose(template="hardware.templates.share")
    @exception_handler(error_web,rules="isinstance(tg_exceptions,ValueError)")
    def share(self, sid=''):
        try:
            host_object = Query(Host).get(sid)
        except:
            raise ValueError("Critical: share ID Not Found - %s" % sid)
        devices = {}
        for dev in host_object.devices:
            #This is to prevent duplicate devices showing up, in the future,
            #There will be no dups in the database
            devices[dev.device_id] = (dev.device, dev.rating)
        ven = DeviceMap('pci')
        return dict(host_object=host_object, devices=devices, \
                    ven=ven, rating_options=rating_options)

    @expose(template="hardware.templates.delete")
    @exception_handler(error_client,rules="isinstance(tg_exceptions,ValueError)")
    def delete(self, UUID=''):
        try:
            host = Query(Host).selectone_by(uuid=UUID)
        except:
            raise ValueError("Critical: UUID does not exist %s " % UUID)
        try:
            ctx.current.delete(host)
            ctx.current.flush()
        except:
            raise ValueError("Critical: Could not delete UUID - Please contact the smolt development team")
        raise ValueError('Success: UUID Removed')

    @expose(template="hardware.templates.token", allow_json=True)
    def token(self, UUID):
        crypt = XOR.new(CRYPTPASS)
        str = "%s\n%s " % ( int(time.mktime(datetime.now().timetuple())), UUID)
        # I hate obfuscation.  Its all I've got
        token = crypt.encrypt(str)
        return dict(token=urllib.quote(token),
                    prefered_protocol=".91")

    @expose("json")
    def token_json(self, uuid):
        crypt = XOR.new(CRYPTPASS)
        str = "%s\n%s " % ( int(time.mktime(datetime.now().timetuple())), uuid)
        # I hate obfuscation.  Its all I've got
        token = crypt.encrypt(str)
        return dict(token=urllib.quote(token),
                    prefered_protocol=currentSmoltProtocol)

    @expose(template="hardware.templates.my_hosts")
    @identity.require(identity.not_anonymous())
    def my_hosts(self):
        try:
            link_sql = Query(FasLink).selectone_by(user_name=identity.current.user_name)
        except InvalidRequestError:
            link_sql = []
        return dict(link_sql=link_sql)

    @expose(template="hardware.templates.link")
    @identity.require(identity.not_anonymous())
    def link(self, UUID):
        try:
            host_sql = Query(Host).selectone_by(uuid=UUID)
        except InvalidRequestError:
            raise ValueError("Critical: Your UUID did not exist.")
        
        if host_sql.fas_account == None:
            link_sql = FasLink(uuid=UUID, user_name=identity.current.user_name)
            ctx.current.flush()
        return dict()
    
    def check_token(self, token, uuid):
        token = urllib.unquote(token)
        crypt = XOR.new(CRYPTPASS)
        token_plain = crypt.decrypt(token).split('\n')
        token_time = int(token_plain[0])
        token_uuid = token_plain[1]
        current_time = int(time.mktime(datetime.now().timetuple()))
        if current_time - token_time > 20:
            raise ValueError("Critical [20]: Invalid Token")
        if uuid.strip() != token_uuid.strip():
            raise ValueError("Critical [s]: Invalid Token")

    @expose()
    @exception_handler(error_client,rules="isinstance(tg_exceptions,ValueError)")
    def add(self, UUID, OS, platform, bogomips, systemMemory, \
            systemSwap, CPUVendor, CPUModel, numCPUs, CPUSpeed, language, \
            defaultRunlevel, vendor, system, token, lsbRelease='Deprecated', \
            formfactor='Unknown', kernelVersion='', selinux_enabled='False', \
            selinux_enforce='Disabled', smoltProtocol=None):
        """Adds a host sans devices to the database
        
        This method is DEPRECATED like there is no tomorrow.  For Marty McFly
        this may be true.
        
        the paramaters are pretty self explanatory so usage is left as
        an excuse to the reader who appreciates old broken things.
        
        It will probably remain through a few releases for older clients.
        """
        if smoltProtocol < ".91":
            raise ValueError("Critical: Outdated smolt client.  Please upgrade.")
        if smoltProtocol > ".91":
            raise ValueError("Woah there marty mcfly, you got to go back to 1955!")
        
        self.check_token(token, UUID)

        uuid = UUID.strip()
        try:
            host_sql = Query(Host).selectone_by(uuid=uuid)
        except InvalidRequestError:
            host_sql = Host()
            host_sql.uuid = uuid

        host_sql.os = OS.strip()
        host_sql.platform = platform.strip()
        try:
            host_sql.bogomips = float(bogomips)
        except:
            host_sql.bogomips = 0
        host_sql.system_memory = int(systemMemory)
        host_sql.system_swap = int(systemSwap)
        host_sql.cpu_vendor = CPUVendor.strip()
        host_sql.cpu_model = CPUModel.strip()
        host_sql.num_cpus = int(numCPUs)
        host_sql.cpu_speed = float(CPUSpeed)
        host_sql.language = language.strip()
        host_sql.default_runlevel = int(defaultRunlevel)
        host_sql.vendor = vendor.strip()
        host_sql.system = system.strip()
        host_sql.kernel_version = kernelVersion.strip()
        host_sql.formfactor = formfactor.strip()
        host_sql.selinux_enabled = bool(selinux_enabled)
        host_sql.selinux_enforce = selinux_enforce.strip()
        host_sql.last_modified = DateTime.now()
        
        ctx.current.flush()
        return dict()

    @expose()
    @exception_handler(error_client, rules="isinstance(tg_exceptions,ValueError)")
    def addDevices(self, UUID, Devices):
        import time
        from mx import DateTime
        try:
            host = Query(Host).selectone_by(uuid=UUID)
        except InvalidRequestError:
            raise ValueError("Critical: UUID not found - %s" % UUID)
        # Read in device id's from the device bulk script
        for device in Devices.split('\n'):
            if not device:
                continue
            try:
                (vendor_id, 
                device_id,
                subsys_vendor_id,
                subsys_device_id,
                bus,
                driver,
                cls,
                description) = device.split('|')
            except:
                raise ValueError("Critical: Device Read Failed - %s" % device)

            # Create Device
            try:
                vendor_id = int(vendor_id)
            except ValueError:
                vendor_id = None
            try:
                subsys_device_id = int(subsys_device_id)
            except ValueError:
                subsys_device_id = None
            try:
                subsys_vendor_id = int(subsys_vendor_id)
            except ValueError:
                subsys_vendor_id = None
            
            #special case in the DB
            if cls is None:
                cls = "NONE"
            
#            if device_id and vendor_id:
#                description = '%s:%s:%s:%s' % (vendor_id, device_id, subsys_device_id, subsys_vendor_id)
            try:
                device_sql = Query(ComputerLogicalDevice)\
                                .selectone_by(device_id=device_id,
                                              vendor_id=vendor_id,
                                              subsys_vendor_id=subsys_vendor_id,
                                              subsys_device_id=subsys_device_id,
                                              description=description)
            except InvalidRequestError:
                try:
                    device_sql = ComputerLogicalDevice()
                    device_sql.bus = bus
                    device_sql.driver = driver
                    device_sql.device_id = device_id
                    device_sql.vendor_id = vendor_id
                    device_sql.subsys_vendor_id = subsys_vendor_id
                    device_sql.subsys_device_id = subsys_device_id
                    device_sql.date_added = DateTime.now()
                    device_sql.description = description
                    
                    try: 
                        class_sql = Query(HardwareClass).selectone_by(cls=cls)
                        device_sql.hardware_class = class_sql
                    except InvalidRequestError:
                        class_sql = HardwareClass()
                        class_sql.cls = cls
                        class_sql.description = "Fill me in!"
                        device_sql.hardware_class = class_sql
                        ctx.current.flush()
                    
                    ctx.current.flush()
                except AttributeError, e:
                    raise ValueError("Critical: Device add Failed - %s" % e)
            except AttributeError, e:
                raise ValueError("Critical: Device add Failed - %s" % e)
            try:
                link = HostLink()
                link.host = host
                link.device = device_sql
            except:
               raise ValueError("Critical: Could not add device: %s" % description)
            ctx.current.flush()
        return dict()
    
    @expose()
    @exception_handler(error_client, rules="isinstance(tg_exceptions,ValueError)")
    def add_json(self, uuid, host, token, smolt_protocol):
        if smolt_protocol < currentSmoltProtocol:
            raise ValueError("Critical: Outdated smolt client.  Please upgrade.")
        if smolt_protocol > currentSmoltProtocol:
            raise ValueError("Woah there marty mcfly, you got to go back to 1955!")
        
        self.check_token(token, uuid)

        host_dict = simplejson.loads(host)
        
        try:
            host_sql = Query(Host).selectone_by(uuid=uuid)
        except InvalidRequestError:
            host_sql = Host()
        host_sql.uuid = host_dict["uuid"]
        host_sql.os = host_dict['os']
        host_sql.default_runlevel = host_dict['default_runlevel']
        host_sql.language = host_dict['language']
        host_sql.platform = host_dict['platform']
        host_sql.bogomips = host_dict['bogomips']
        host_sql.cpu_vendor = host_dict['cpu_vendor']
        host_sql.cpu_model = host_dict['cpu_model']
        host_sql.cpu_speed = host_dict['cpu_speed']
        host_sql.num_cpus = host_dict['num_cpus']
        host_sql.system_memory = host_dict['system_memory']
        host_sql.system_swap = host_dict['system_swap']
        host_sql.vendor = host_dict['vendor']
        host_sql.system = host_dict['system']
        host_sql.kernel_version = host_dict['kernel_version']
        host_sql.formfactor = host_dict['formfactor']
        host_sql.selinux_enabled = host_dict['selinux_enabled']
        host_sql.selinux_enforce = host_dict['selinux_enforce']
        
                
        orig_devices = [device.device_id for device 
                                         in host_sql.devices]
        
        
        for device in host_dict['devices']:
            description = device['description']
            device_id = device['device_id']
            if device_id is None:
                device_id = 0
            vendor_id = device['vendor_id']
            if vendor_id is None:
                vendor_id = 0
            subsys_vendor_id = device['subsys_vendor_id']
            if subsys_vendor_id is None:
                subsys_vendor_id = 0
            subsys_device_id = device['subsys_device_id']
            if subsys_device_id is None:
                subsys_device_id = 0
            try:
                device_sql = Query(ComputerLogicalDevice)\
                    .selectone_by(device_id=device_id,
                                  vendor_id=vendor_id,
                                  subsys_vendor_id=subsys_vendor_id,
                                  subsys_device_id=subsys_device_id,
                                  description=description)
                if device_sql.id in orig_devices:
                    orig_devices.remove(device_sql.id)
                else:
                    host_link_sql = HostLink()
                    host_link_sql.host = host_sql
                    host_link_sql.device = device_sql
                    hl = host_link_sql
            except InvalidRequestError:
                cls = device['type']
                if cls is None:
                    cls = "NONE"
                device_sql = ComputerLogicalDevice()
                device_sql.device_id = device_id
                device_sql.vendor_id = vendor_id
                device_sql.subsys_vendor_id = subsys_vendor_id
                device_sql.subsys_device_id = subsys_device_id
                device_sql.bus = device['bus']
                device_sql.driver = device['driver']
                device_sql.cls = cls
                device_sql.description = device['description']
                device_sql.date_added = DateTime.now() 
                
                d = device_sql
                
                try: 
                    class_sql = Query(HardwareClass).selectone_by(cls=cls)
                    device_sql.hardware_class = class_sql
                except InvalidRequestError:
                    class_sql = HardwareClass()
                    class_sql.cls = cls
                    class_sql.class_description = "Fill me in!"
                    device_sql.hardware_class = class_sql
                    ctx.current.flush()
                    
                ctx.current.flush()
               
                host_link = HostLink()
                host_link.host = host_sql
                host_link.device = device_sql
            
        for device_sql_id in orig_devices:
            bad_host_link = Query(HostLink)\
                .select_by(device_id=device_sql_id,
                           host_link_id=host_sql.id)
            if bad_host_link and len(bad_host_link):
                ctx.current.delete(bad_host_link[0])
        ctx.current.flush()
        
        return dict()
    
    @expose(template="hardware.templates.not_loaded")
    def unavailable(self, tg_exceptions=None):
        return dict()
        
    @expose()
    def rate_object(self, *args, **kwargs):
        #log.info('args = %s' % str(args))
        #log.info('kwargs = %s' % str(kwargs))
        id = kwargs.get("ratingID")
        rating = kwargs.get("value")
        if id.startswith("Host"):
            sep = id.find("_")
            if sep == -1:
                host_id = id[4:]
                host = Query(Host).selectone_by(uuid=host_id)
                host.rating = int(rating)
                ctx.current.flush()
                return dict()
                
            host_id = id[4:sep]
            id = id[sep+1:]
            if id.startswith("Device"):
                device_id = int(id[6:])
                host = Query(Host).selectone_by(uuid=host_id)
                for device in host.devices:
                    if device.device_id == device_id:
                        device.rating = int(rating)
                        ctx.current.flush([host, device])
                        return dict()
        return dict()
