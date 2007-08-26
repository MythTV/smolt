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

from hardware.model import *
from hwdata import DeviceMap
from smoonexceptions import NotCachedException
from lock.multilock import MultiLock

# This is such a bad idea, yet here it is.
CRYPTPASS = 'PleaseChangeMe11'
currentSmoltProtocol = '0.97' 

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
class Root(controllers.RootController):
    def __init__(self):
        controllers.RootController.__init__(self)
        self.devices_lock = MultiLock()
        self.stats_lock = MultiLock()
        scheduler.add_interval_task(action=self.write_devices, interval=1800, \
                                    args=None, kw=None, initialdelay=15, \
                                    processmethod=scheduler.method.threaded, \
                                    taskname="devices_cache")
        scheduler.add_interval_task(action=self.write_stats, interval=300, \
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
        try:
            uuid = u'%s' % UUID.strip()
            uuid = uuid.encode('utf8')
        except:
            raise ValueError("Critical: Unicode Issue - Tell Mike!")
        try:
            host_object = Query(Host).selectone_by(uuid=UUID)
        except:
            raise ValueError("Critical: UUID Not Found - %s" % UUID)
        devices = {}
        for dev in host_object.devices:
            #This is to prevent duplicate devices showing up, in the future,
            #There will be no dups in the database
            devices[dev.device_id] = (dev.device, dev.rating)
        ven = DeviceMap('pci')
        return dict(host_object=host_object, devices=devices, ven=ven, rating=rating)

    @expose(template="hardware.templates.delete")
    @exception_handler(error_client,rules="isinstance(tg_exceptions,ValueError)")
    def delete(self, UUID=''):
        try:
            host = Query(Host).selectone_by(uuid=UUID)
        except:
            raise ValueError("Critical: UUID does not exist %s " % UUID)
        try:
            host.delete()
            host.flush()
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
            link_sql.flush()
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
            
#            if device_id and vendor_id:
#                description = '%s:%s:%s:%s' % (vendor_id, device_id, subsys_device_id, subsys_vendor_id)
            try:
                device_sql = Query(ComputerLogicalDevice).selectone_by(description=description)
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
            print "closing up shop"
            print "flushing link"
            print "flushing device"
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
            host_sql = Host.selectone_by(uuid=uuid)
            host_sql.delete()
            host_sql.flush()
            host_sql = Host()
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
                
        for device in host_dict['devices']:
            try:
                device_sql = ComputerLogicalDevice.selectone_by(description=device['description'])
            except InvalidRequestError:
                device_sql = ComputerLogicalDevice()
                device_sql.device_id = device['device_id']
                device_sql.subsys_vendor_id = device['subsys_vendor_id']
                device_sql.subsys_device_id = device['subsys_device_id']
                device_sql.bus = device['bus']
                device_sql.driver = device['driver']
                device_sql.type = device['type']
                device_sql.description = device['description']
                device_sql.date_added = DateTime.now()  
                device_sql.save_or_update()
                device_sql.flush()

            
            host_link = HostLink()
            host_link.host = host_sql
            host_link.device = device_sql
            host_link.save_or_update()
            host_link.flush()
            
        host_sql.save_or_update()
        host_sql.flush()
        host_sql.refresh()

        
        return dict()
    
    @expose(template="hardware.templates.deviceclass", allow_json=True)
    def by_class(self, type='VIDEO'):
        type = type.encode('utf8')
        #classes = Host._connection.queryAll('select distinct(class) from device;')
        try:
            cls = HardwareClass.query().selectone_by(cls=type)
        except InvalidRequestError:
            return (None, )
        pci_vendors = DeviceMap('pci')
        tabs = Tabber()
        # We only want hosts that detected hardware (IE, hal was working properly)
        total_hosts = select([host_links.c.host_link_id], distinct=True).alias("m").count().execute().fetchone()[0]
        count = select([host_links.c.host_link_id], and_(host_links.c.device_id == computer_logical_devices.c.id, computer_logical_devices.c.cls == type), distinct=True).alias("m").count().execute().fetchone()[0]
        types = HardwareByClass.query().order_by(desc(HardwareByClass.c.count)).limit(100).select_by(cls=type)
        device = computer_logical_devices
        vendors = select([func.count(device.c.vendor_id).label('cnt'), device.c.vendor_id], device.c.cls==type, order_by=[desc('cnt')], group_by=device.c.vendor_id).execute().fetchall()
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
        devices['total'] = HostLink.query().count()
        devices['count'] = ComputerLogicalDevice.query().count()
        devices['total_hosts'] = Host.query().count()
        devices['totalList'] = TotalList.query().select(limit=100)
        devices['uniqueList'] = UniqueList.query().select(limit=100)
        devices['classes'] = HardwareClass.query().select()
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
        stats['total_hosts'] = Host.query().count()
        total_hosts = stats['total_hosts']
        stats['archs'] = Arch.query().select()
        stats['os'] = OS.query().select(limit=15)
        stats['runlevel'] = Runlevel.query().select()
        stats['num_cpus'] = NumCPUs.query().select()
        stats['vendors'] = Vendor.query().select(limit=100)
        stats['systems'] = System.query().select(limit=100)
        stats['cpu_vendor'] = CPUVendor.query().select(limit=100)
        stats['kernel_version'] = KernelVersion.query().select(limit=20)
        stats['formfactor'] = FormFactor.query().select()
        stats['language'] = Language.query().select()
        stats['languagetot'] = stats['total_hosts']
 
        stats['sys_mem'] = []
        stats['sys_mem'].append(("less than 512mb", Host.query().filter(Host.c.system_memory<512).count()))
        stats['sys_mem'].append(("between 512mb and 1023mb", Host.query().filter(and_(Host.c.system_memory>=512, Host.c.system_memory<1024)).count()))
        stats['sys_mem'].append(("between 1024mb and 2047mb", Host.query().filter(and_(Host.c.system_memory>=1024, Host.c.system_memory<2048)).count()))
        stats['sys_mem'].append(("more than 2048mb", Host.query().filter(Host.c.system_memory>=2048).count()))

        stats['swap_mem'] = []
        stats['swap_mem'].append(("less than 512mb", Host.query().filter(Host.c.system_swap<512).count()))
        stats['swap_mem'].append(("between 512mb and 1027mb", Host.query().filter(and_(Host.c.system_swap>=512, Host.c.system_swap<1024)).count()))
        stats['swap_mem'].append(("between 1024mb and 2047mb", Host.query().filter(and_(Host.c.system_swap>=1024, Host.c.system_swap<2048)).count()))
        stats['swap_mem'].append(("more than 2048mb", Host.query().filter(Host.c.system_swap>=2048).count()))

        stats['cpu_speed'] = []
        stats['cpu_speed'].append(("less than 512mhz", Host.query().filter(Host.c.cpu_speed<512).count()))
        stats['cpu_speed'].append(("between 512mhz and 1023mhz", Host.query().filter(and_(Host.c.cpu_speed>=512, Host.c.cpu_speed<1024)).count()))
        stats['cpu_speed'].append(("between 1024mhz and 2047mhz", Host.query().filter(and_(Host.c.cpu_speed>=1024, Host.c.cpu_speed<2048)).count()))
        stats['cpu_speed'].append(("more than 2048mhz", Host.query().filter(Host.c.cpu_speed>=2048).count()))

        stats['bogomips'] = []
        stats['bogomips'].append(("less than 512", Host.query().filter(Host.c.bogomips<512).count()))
        stats['bogomips'].append(("between 512 and 1023", Host.query().filter(and_(Host.c.bogomips>=512, Host.c.bogomips<1024)).count()))
        stats['bogomips'].append(("between 1024 and 2047", Host.query().filter(and_(Host.c.bogomips>=1024, Host.c.bogomips<2048)).count()))
        stats['bogomips'].append(("between 2048 and 4000", Host.query().filter(and_(Host.c.bogomips>=2048, Host.c.bogomips<4000)).count()))
        stats['bogomips'].append(("more than 4000", Host.query().filter(Host.c.system_memory>=4000).count()))

        stats['bogomips_total'] = Host.query().filter(Host.c.bogomips > 0).sum(Host.c.bogomips * Host.c.num_cpus)
        stats['cpu_speed_total'] = Host.query().filter(Host.c.cpu_speed > 0).sum(Host.c.cpu_speed * Host.c.num_cpus)
        stats['cpus_total'] = Host.query().sum(Host.c.num_cpus)
        stats['registered_devices'] = ComputerLogicalDevice.query().count()

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
    def submit_ratings(self, uuid, **kw):
        
        try:
            host = Host.query().selectone_by(uuid=uuid)
        except InvalidRequestError:
            redirect("error_client")
        host.rating = int(kw["host_rating"])
        
        
        for (device_key, rating) in kw.items():
            if device_key.startswith("device_"):
               device_ref = device_key[7:]
               device_db_ref = int(device_ref)
               for device in host.devices:
                   if device.device_id == device_db_ref:
                       device.rating = int(rating)
        host.save_or_update()
        host.flush()
        flash("Ratings Saved!")
        redirect("show?UUID=%s" % uuid)
            
            

