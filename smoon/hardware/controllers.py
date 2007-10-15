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
from lock.multilock import MultiLock

import logging
log = logging.getLogger("smoon")

# This is such a bad idea, yet here it is.
CRYPTPASS = 'PleaseChangeMe11'
currentSmoltProtocol = '0.97' 

def getWikiLink(bus, vendor_id, device_id, subsys_vendor_id, subsys_device_id):
    return '/wiki/%s/%04x/%04x/%04x/%04x' % (bus,
                                             int(vendor_id or 0),
                                             int(device_id or 0),
                                             int(subsys_vendor_id or 0),
                                             int(subsys_vendor_id or 0))

class SingleSelectField(widgets.SingleSelectField):
    """This class is a workaround for TG which does not properly process
    the field_id param on the SingleSelectField widget.
    """
    def update_params(self, d):
        """For some reason, field_id, and name are both proper parameters
        in the kid template for this widget, however, they are not allowed
        to be configured at display time, only at widget creation time.
        understanding that widgets should be as stateless as possible, this
        allows you to declare new values at display time
        """
        if "field_id" in d:
            field_id = d["field_id"]
        else:
            field_id = ""
        super(SingleSelectField, self).update_params(d)
        if not field_id == "":
            d["field_id"] = field_id
            d['name'] = field_id
    
    params = ["field_id"]

rating = SingleSelectField(options = [(0, "Please Pick One"),
                                      (1, "This breaks stuff"),
                                      (2, "This doesn't work"),
                                      (3, "This sorta works"),
                                      (4, "This works great! ^_^")])
rating_options = {0: "Not Rated",
                  1: "This breaks stuff",
                  2: "This doesn't work",
                  3: "This sorta works :-/",
                  4: "This works great! ^_^",
                  5: "Mike is awesome"}

class ByClass(object):
    def __init__(self):
        self.rw_lock = MultiLock()
        self.data = {}
        scheduler.add_interval_task(action=self.fetch_data, interval=21600, \
                                    args=None, kw=None, initialdelay=60, \
                                    processmethod=scheduler.method.threaded, \
                                    taskname="byclass_cache")
       
    def fetch_data(self):
        classes = Query(HardwareClass).select()
        for cls in classes:
            type = cls.cls
            # We only want hosts that detected hardware (IE, hal was working properly)
            total_hosts = select([host_links.c.host_link_id], distinct=True)\
                            .alias("m").count()\
                            .execute().fetchone()[0]
            count = select([host_links.c.host_link_id], \
                           and_(host_links.c.device_id == computer_logical_devices.c.id, \
                                computer_logical_devices.c.cls == type), \
                           distinct=True).alias("m")\
                     .count().execute().fetchone()[0]
            types = Query(HardwareByClass)\
                        .order_by(desc(HardwareByClass.c.count))\
                        .limit(100).select_by(cls=type)
            device = computer_logical_devices
            vendors = select([func.count(device.c.vendor_id).label('cnt'), \
                              device.c.vendor_id], \
                             device.c.cls==type, order_by=[desc('cnt')], \
                             group_by=device.c.vendor_id)\
                        .execute().fetchall()
            self.rw_lock.write_acquire()
            self.data[type] = (total_hosts, count, types, vendors)
            self.rw_lock.write_release()
    
    def get_data(self, cls):
        try:
            self.rw_lock.read_acquire()
            _return = self.data[cls]
            self.rw_lock.read_release()
        except Exception, e:
            self.rw_lock.read_release()
            raise e
        return _return
    
    def __getitem__(self, key):
        return self.get_data(key)

    pass

class Root(controllers.RootController):
    def __init__(self):
        controllers.RootController.__init__(self)
        self.devices_lock = MultiLock()
        self.stats_lock = MultiLock()
        self.byclass_cache = ByClass()
        scheduler.add_interval_task(action=self.write_devices, interval=21600, \
                                    args=None, kw=None, initialdelay=30, \
                                    processmethod=scheduler.method.threaded, \
                                    taskname="devices_cache")
        scheduler.add_interval_task(action=self.write_stats, interval=10800, \
                                    args=None, kw=None, initialdelay=5, \
                                    processmethod=scheduler.method.threaded, \
                                    taskname="stats_cache")

        
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
        return self.getShow(UUID=UUID)
        
    @expose(template="hardware.templates.showall")
    @exception_handler(error_web,rules="isinstance(tg_exceptions,ValueError)")
    def show_all(self, UUID=''):
        return self.getShow(UUID=UUID)

    def getShow(self, UUID=''):
        try:
            uuid = u'%s' % UUID.strip()
            uuid = uuid.encode('utf8')
        except:
            raise ValueError("Critical: Unicode Issue - Tell Mike!")
        try:
            host_object = Query(Host).selectone_by(uuid=UUID)
            ctx.current.refresh(host_object)
        except:
            raise ValueError("Critical: UUID Not Found - %s" % UUID)
        devices = {}
        for dev in host_object.devices:
            ctx.current.refresh(dev)
            #This is to prevent duplicate devices showing up, in the future,
            #There will be no dups in the database
            devices[dev.device_id] = (dev.device, dev.rating)
        ven = DeviceMap('pci')
        return dict(host_object=host_object,
                    devices=devices, ven=ven,
                    ratingwidget=SingleRatingWidget(),
                    getWikiLink = getWikiLink,
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
                           host_link_id=host_sql.id)[0]
            ctx.current.delete(bad_host_link)
        ctx.current.flush()
        
        return dict()
    
    @expose(template="hardware.templates.deviceclass", allow_json=True)
    def by_class(self, type='VIDEO'):
        type = type.encode('utf8')
        #classes = Host._connection.queryAll('select distinct(class) from device;')
        pci_vendors = DeviceMap('pci')
        tabs = Tabber()
        # We only want hosts that detected hardware (IE, hal was working properly)
#        total_hosts = select([host_links.c.host_link_id], distinct=True).alias("m").count().execute().fetchone()[0]
#        count = select([host_links.c.host_link_id], and_(host_links.c.device_id == computer_logical_devices.c.id, computer_logical_devices.c.cls == type), distinct=True).alias("m").count().execute().fetchone()[0]
#        types = Query(HardwareByClass).order_by(desc(HardwareByClass.c.count)).limit(100).select_by(cls=type)
#        device = computer_logical_devices
#        vendors = select([func.count(device.c.vendor_id).label('cnt'), device.c.vendor_id], device.c.cls==type, order_by=[desc('cnt')], group_by=device.c.vendor_id).execute().fetchall()
        try:
            (total_hosts, count, types, vendors) = self.byclass_cache[type]
        except KeyError:
            raise redirect('unavailable')
        return dict(types=types, type=type, total_hosts=total_hosts, count=count, pci_vendors=pci_vendors, vendors=vendors, tabs=tabs)

    @expose(template="hardware.templates.not_loaded")
    def unavailable(self, tg_exceptions=None):
        return dict()

    @expose(template="hardware.templates.devices")
#    @exception_handler(not_ready_handler, rules="isinstance(tg_exceptions,smoonexceptions.NotCachedException")
# This seems to be borked, but it is the correct way to do things.  I will
# now demonstrate a better, but incorrect way.  Moof.
    def devices(self):
        try:
            devices = self.read_devices()
        except:
            raise redirect("unavailable")
        tabs = Tabber()
        return dict(devices=devices, tabs=tabs)
    
    def read_devices(self):
        self.devices_lock.read_acquire()
        try:
            _return = self._devices_cache.copy()
        except AttributeError:
            self.devices_lock.read_release()
            raise NotCachedException
        else:
            self.devices_lock.read_release()
        return _return
    
    def write_devices(self):
        devices = {}
        devices['total'] = Query(HostLink).count()
        devices['count'] = Query(ComputerLogicalDevice).count()
        devices['total_hosts'] = Query(Host).count()
        devices['totalList'] = Query(TotalList).select(limit=100)
        devices['uniqueList'] = Query(UniqueList).select(limit=100)
        devices['classes'] = Query(HardwareClass).select()
        self.devices_lock.write_acquire()
        self._devices_cache = devices
        self.devices_lock.write_release()
        pass

    def read_stats(self):
        self.stats_lock.read_acquire()
        try:
            _return = self._stats_cache.copy()
        except AttributeError:
            self.stats_lock.read_release()
            raise NotCachedException
        else:
            self.stats_lock.read_release()
        return _return


    def write_stats(self):
        self.stats_lock.write_acquire()
        stats = {}
        stats['total_hosts'] = Query(Host).count()
        total_hosts = stats['total_hosts']
        stats['archs'] = Query(Arch).select()
        stats['os'] = Query(OS).select(limit=15)
        stats['runlevel'] = Query(Runlevel).select()
        stats['num_cpus'] = Query(NumCPUs).select()
        stats['vendors'] = Query(Vendor).select(limit=100)
        stats['systems'] = Query(System).select(limit=100)
        stats['cpu_vendor'] = Query(CPUVendor).select(limit=100)
        stats['kernel_version'] = Query(KernelVersion).select(limit=20)
        stats['formfactor'] = Query(FormFactor).select()
        stats['language'] = Query(Language).select()
        stats['languagetot'] = stats['total_hosts']
 
        stats['sys_mem'] = []
        stats['sys_mem'].append(("less than 256mb", Query(Host).filter(Host.c.system_memory<256).count()))
        stats['sys_mem'].append(("between 256mb and 512mb", Query(Host).filter(and_(Host.c.system_memory>=256, Host.c.system_memory<512)).count()))
        stats['sys_mem'].append(("between 512mb and 1023mb", Query(Host).filter(and_(Host.c.system_memory>=512, Host.c.system_memory<1024)).count()))
        stats['sys_mem'].append(("between 1024mb and 2047mb", Query(Host).filter(and_(Host.c.system_memory>=1024, Host.c.system_memory<2048)).count()))
        stats['sys_mem'].append(("more than 2048mb", Query(Host).filter(Host.c.system_memory>=2048).count()))

        stats['swap_mem'] = []
        stats['swap_mem'].append(("less than 512mb", Query(Host).filter(Host.c.system_swap<512).count()))
        stats['swap_mem'].append(("between 512mb and 1027mb", Query(Host).filter(and_(Host.c.system_swap>=512, Host.c.system_swap<1024)).count()))
        stats['swap_mem'].append(("between 1024mb and 2047mb", Query(Host).filter(and_(Host.c.system_swap>=1024, Host.c.system_swap<2048)).count()))
        stats['swap_mem'].append(("more than 2048mb", Query(Host).filter(Host.c.system_swap>=2048).count()))

        stats['cpu_speed'] = []
        stats['cpu_speed'].append(("less than 512mhz", Query(Host).filter(Host.c.cpu_speed<512).count()))
        stats['cpu_speed'].append(("between 512mhz and 1023mhz", Query(Host).filter(and_(Host.c.cpu_speed>=512, Host.c.cpu_speed<1024)).count()))
        stats['cpu_speed'].append(("between 1024mhz and 2047mhz", Query(Host).filter(and_(Host.c.cpu_speed>=1024, Host.c.cpu_speed<2048)).count()))
        stats['cpu_speed'].append(("more than 2048mhz", Query(Host).filter(Host.c.cpu_speed>=2048).count()))

        stats['bogomips'] = []
        stats['bogomips'].append(("less than 512", Query(Host).filter(Host.c.bogomips<512).count()))
        stats['bogomips'].append(("between 512 and 1023", Query(Host).filter(and_(Host.c.bogomips>=512, Host.c.bogomips<1024)).count()))
        stats['bogomips'].append(("between 1024 and 2047", Query(Host).filter(and_(Host.c.bogomips>=1024, Host.c.bogomips<2048)).count()))
        stats['bogomips'].append(("between 2048 and 4000", Query(Host).filter(and_(Host.c.bogomips>=2048, Host.c.bogomips<4000)).count()))
        stats['bogomips'].append(("more than 4000", Query(Host).filter(Host.c.system_memory>=4000).count()))

        stats['bogomips_total'] = Query(Host).filter(Host.c.bogomips > 0).sum(Host.c.bogomips * Host.c.num_cpus)
        stats['cpu_speed_total'] = Query(Host).filter(Host.c.cpu_speed > 0).sum(Host.c.cpu_speed * Host.c.num_cpus)
        stats['cpus_total'] = Query(Host).sum(Host.c.num_cpus)
        stats['registered_devices'] = Query(ComputerLogicalDevice).count()

        self._stats_cache = stats
        self.stats_lock.write_release()

    @expose(template="hardware.templates.stats")
    def stats(self):
        try:
            stats = self.read_stats()
        except:
            raise redirect("unavailable")
        tabs = Tabber()
        return dict(stat=stats, tabs=tabs, total_hosts=stats['total_hosts'])
    
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
            host = Query(Host).selectone_by(uuid=host_id)
            id = id[sep+1:]
            if id.startswith("Device"):
                device_id = int(id[6:])
                for device in host.devices:
                    if device.device_id == device_id:
                        device.rating = int(rating)
                ctx.current.flush()
        return dict()
