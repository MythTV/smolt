#!/usr/bin/python
__requires__ = "Turbogears[future]"
import pkg_resources
pkg_resources.require("TurboGears")

from turbogears.view import engines
import turbogears.view
import turbogears.util as tg_util
from turbogears import view, database, errorhandling, config
from itertools import izip
from inspect import isclass
from turbogears import update_config, start_server
import cherrypy
cherrypy.lowercase_api = True
from os.path import *
import sys
import time
from hardware.wiki import *
from turboflot import TurboFlot

# first look on the command line for a desired config file,
# if it's not on the command line, then
# look for setup.py in this directory. If it's not there, this script is
# probably installed
if len(sys.argv) > 1:
    update_config(configfile=sys.argv[1],
        modulename="hardware.config")
elif exists(join(dirname(__file__), "setup.py")):
    update_config(configfile="dev.cfg",modulename="hardware.config")
else:
    update_config(configfile="prod.cfg",modulename="hardware.config")

from sqlalchemy import *

from hardware.model import *
from hardware.hwdata import DeviceMap

#bind = metadata.bind
from turbogears.widgets import Tabber
tabs = Tabber()

# the path, where to store the generated pages
page_path = "hardware/static/stats"

engine = engines.get('genshi', None)
turbogears.view.load_engines()
#template config vars
template_config={}
template_config['archs']=config.get("stats_template.archs", [])
template_config['os']=config.get("stats_template.os", [])
template_config['runlevel']=config.get("stats_template.runlevel", [])
template_config['lang']=config.get("stats_template.lang", [])
template_config['vendors']=config.get("stats_template.vendors", [])
template_config['model']=config.get("stats_template.model", [])
template_config['ram']=config.get("stats_template.ram", [])
template_config['swap']=config.get("stats_template.swap", [])
template_config['cpu']=config.get("stats_template.cpu", [])
template_config['kernel']=config.get("stats_template.kernel", [])
template_config['formfactor']=config.get("stats_template.formfactor", [])
template_config['selinux']=config.get("stats_template.selinux", [])
template_config['filesystem']=config.get("stats_template.filesystem", [])
template_config['mythrole']=config.get("stats_template.mythrole", [])
template_config['mythremote']=config.get("stats_template.mythremote", [])
template_config['myththeme']=config.get("stats_template.myththeme", [])

def _process_output(output, template, format):
    """Produces final output form from the data returned from a
    controller method.

    @param tg_format: format of desired output (html or json)
    @param output: the output returned by the controller
    @param template: HTML template to use
    """
    if isinstance(output, dict):
        from turbogears.widgets import js_location

        css = tg_util.setlike()
        js = dict(izip(js_location, iter(tg_util.setlike, None)))
        include_widgets = {}
        include_widgets_lst = config.get("tg.include_widgets", [])

        if config.get("tg.mochikit_all", False):
            include_widgets_lst.insert(0, 'turbogears.mochikit')

        for i in include_widgets_lst:
            widget = tg_util.load_class(i)
            if isclass(widget):
                widget = widget()
            include_widgets["tg_%s" % i.split(".")[-1]] = widget
            for script in widget.retrieve_javascript():
                if hasattr(script, "location"):
                    js[script.location].add(script)
                else:
                    js[js_location.head].add(script)
            css.add_all(widget.retrieve_css())

        for value in output.itervalues():
            if hasattr(value, "retrieve_css"):
                retrieve = getattr(value, "retrieve_css")
                if callable(retrieve):
                    css.add_all(value.retrieve_css())
            if hasattr(value, "retrieve_javascript"):
                retrieve = getattr(value, "retrieve_javascript")
                if callable(retrieve):
                    for script in value.retrieve_javascript():
                        if hasattr(script, "location"):
                            js[script.location].add(script)
                        else:
                            js[js_location.head].add(script)
        output.update(include_widgets)
        output["tg_css"] = css
        #output.update([("tg_js_%s" % str(l), js[l]) for l in js_location])
        for l in iter(js_location):
            output["tg_js_%s" % str(l)] = js[l]

        output["tg_flash"] = output.get("tg_flash")

        return engine.render(output, format=format, template=template)



stats = {}
# somehow this has to be first, cause it binds us to
# an sqlalchemy context
print 'total_hosts'
stats['total_hosts'] = session.query(Host).count()

class ByClass(object):
    def __init__(self):
        self.data = {}

    def fetch_data(self):
        classes = session.query(HardwareClass).select()
        count = {}
        types = {}
        vendors = {}
        total_hosts = 0

        # We only want hosts that detected hardware (IE, hal was working properly)
        print 'Device: total_host with hardware'
        total_hosts = select([func.count(func.distinct(host_links.c.host_link_id))])\
                      .execute().fetchone()[0]

        for cls in classes:
            type = cls.cls

            #devs = select([computer_logical_devices], computer_logical_devices.c.cls == type).alias("devs")
            devs = computer_logical_devices
            print 'Device: %s types' % type
            Device=select([ComputerLogicalDevice.c.id, ComputerLogicalDevice.c.description,
              ComputerLogicalDevice.c.bus, ComputerLogicalDevice.c.driver,
              ComputerLogicalDevice.c.cls, ComputerLogicalDevice.c.date_added,
              ComputerLogicalDevice.c.device_id, ComputerLogicalDevice.c.vendor_id,
              ComputerLogicalDevice.c.subsys_device_id,
              ComputerLogicalDevice.c.subsys_vendor_id],
              ComputerLogicalDevice.c.cls==type).alias('d')
            types = select([Device, func.count(HostLink.c.host_link_id.distinct()
                    ).label('count')], Device.c.id==HostLink.c.device_id).group_by(Device.c.id)\
                    .order_by(desc('count')).limit(100).execute().fetchall()
#            types = select([devs,
#                            func.count(func.distinct(host_links.c.host_link_id)).label('c')],
#                           and_(devs.c.cls == type,
#                                host_links.c.device_id == devs.c.id),
#                           #from_obj=[ host_links.join(devs, host_links.c.device_id == devs.c.id) ],
#                           group_by=host_links.c.device_id,
#                           order_by=[desc('c')],
#                           limit=100).execute().fetchall();

#            devs = select([computer_logical_devices.c.id],
#                          and_(computer_logical_devices.c.cls == type,
#                               old_hosts_clause())).alias("devs")
#            devs = computer_logical_devices
            print 'Device: %s count' % type
            count = select([func.count(func.distinct(host_links.c.host_link_id))],
                           and_(devs.c.cls == type,
                                host_links.c.device_id == devs.c.id)).execute().fetchone()[0]

            device = computer_logical_devices
            print 'Device: %s vendors' % type
            vendors = select([func.count(device.c.vendor_id).label('cnt'),
                              device.c.vendor_id],
                             device.c.cls==type,
                             order_by=[desc('cnt')],
                             group_by=device.c.vendor_id).execute().fetchall()

            self.data[type] = (total_hosts, count, types, vendors)


    def __getitem__(self, key):
        return self.data[key]

    pass


byclass_cache = ByClass()
byclass_cache.fetch_data()

for type in byclass_cache.data.keys():
    type=type
    pci_vendors = DeviceMap('pci')
    (total_hosts, count, types, vendors) = byclass_cache[type]
    engine = engines.get('genshi', None)
    t=engine.load_template('hardware.templates.deviceclass')
    out_html = _process_output(dict(types=types, type=type,
                                    total_hosts=total_hosts, count=count,
                                    pci_vendors=pci_vendors, vendors=vendors,
                                    tabs=tabs), template=t, format='html')
    fname = "%s/by_class_%s.html" % (page_path, type)
    f = open(fname, "w")
    f.write(out_html)
    f.close()

# Save some memory
del byclass_cache
del out_html

stats = {}

print 'total_active_hosts'
total_active_hosts = session.query(Host).filter(Host.c.last_modified > (date.today() - timedelta(days=90))).count()

print 'total_hosts'
stats['total_hosts'] = session.query(Host).count()
total_hosts = stats['total_hosts']
flot = {}
# Arch calculation
if not  template_config['archs'] == [] :
    print 'arch stats'
    stats['archs'] = session.query(Arch).select()
    archs = []
    counts = []
    i = 0
    for arch in stats['archs']:
        archs.append([i + .5, arch.platform])
        counts.append([i, arch.cnt])
        i += 1
    flot['archs'] = TurboFlot([
        {   'data' : counts,
            'bars' : { 'show' : True },
            'label' : 'Archs', }],
        {   'xaxis' : { 'ticks' : archs }, } )

print "OS Stats"
if not  template_config['os'] == [] :
    stats['os'] = session.query(OS).select(limit=30)

print "Runlevel stats"
if not  template_config['runlevel'] == [] :
    stats['runlevel'] = session.query(Runlevel).select()

print "Vendor stats"
if not  template_config['vendors'] == [] :
    stats['vendors'] = session.query(Vendor).select(limit=100)

print "Model stats"
if not  template_config['model'] == [] :
    stats['systems'] = session.query(System).select(limit=100)

print "CPU stats"
stats['cpu_vendor'] = session.query(CPUVendor).select(limit=100)

if not  template_config['kernel'] == [] :
    print "Kernel stats"
    stats['kernel_version'] = session.query(KernelVersion).select(limit=20)

if not  template_config['formfactor'] == [] :
    print 'Formfactor stats'
    stats['formfactor'] = session.query(FormFactor).select(limit=8)

if not  template_config['lang'] == [] :
    print 'language stats'
    stats['language'] = session.query(Language).select()

if not  template_config['selinux'] == [] :
    print 'selinux stats'
    stats['selinux_enabled'] = session.query(SelinuxEnabled).select()
    stats['selinux_enforce'] = session.query(SelinuxEnforced).select()
    stats['selinux_policy'] = session.query(SelinuxPolicy).select()


now = date.today() - timedelta(days=90)

if not  template_config['ram'] == [] :
    print 'memory stats'
    stats['sys_mem'] = []
    stats['sys_mem'].append(("less than 256mb",
                            session.query(Host).filter(and_(Host.c.system_memory<256, Host.c.last_modified > (now))).count()))
    stats['sys_mem'].append(("between 256mb and 512mb",
                            session.query(Host).filter(and_(Host.c.system_memory>=256,
                                                    Host.c.system_memory<512, Host.c.last_modified > (now))).count()))
    stats['sys_mem'].append(("between 512mb and 1023mb",
                            session.query(Host).filter(and_(Host.c.system_memory>=512,
                                                    Host.c.system_memory<1024, Host.c.last_modified > (now))).count()))
    stats['sys_mem'].append(("between 1024mb and 2047mb",
                            session.query(Host).filter(and_(Host.c.system_memory>=1024,
                                                    Host.c.system_memory<2048, Host.c.last_modified > (now))).count()))
    stats['sys_mem'].append(("more than 2048mb",
                            session.query(Host).filter(and_(Host.c.system_memory>=2048, Host.c.last_modified > (now))).count()))

if not  template_config['swap'] == [] :
    print 'swap stats'
    stats['swap_mem'] = []
    stats['swap_mem'].append(("less than 512mb",
                            session.query(Host).filter(and_(Host.c.system_swap<512, Host.c.last_modified > (now))).count()))
    stats['swap_mem'].append(("between 512mb and 1027mb",
                            session.query(Host).filter(and_(Host.c.system_swap>=512,
                                                    Host.c.system_swap<1024, Host.c.last_modified > (now))).count()))
    stats['swap_mem'].append(("between 1024mb and 2047mb",
                            session.query(Host).filter(and_(Host.c.system_swap>=1024,
                                                    Host.c.system_swap<2048, Host.c.last_modified > (now))).count()))
    stats['swap_mem'].append(("more than 2048mb",
                            session.query(Host).filter(and_(Host.c.system_swap>=2048, Host.c.last_modified > (now))).count()))

#cpu tab
if not  template_config['cpu'] == [] :
    print 'cpu stats'
    stats['cpu_speed'] = []
    stats['cpu_speed'].append(("less than 512mhz",
                            session.query(Host).filter(Host.c.cpu_speed<512).count()))
    stats['cpu_speed'].append(("between 512mhz and 1023mhz",
                            session.query(Host).filter(and_(Host.c.cpu_speed>=512,
                                                    Host.c.cpu_speed<1024)).count()))
    stats['cpu_speed'].append(("between 1024mhz and 2047mhz",
                            session.query(Host).filter(and_(Host.c.cpu_speed>=1024,
                                                    Host.c.cpu_speed<2048)).count()))
    stats['cpu_speed'].append(("more than 2048mhz",
                            session.query(Host).filter(Host.c.cpu_speed>=2048).count()))

    stats['bogomips'] = []
    stats['bogomips'].append(("less than 512",
                            session.query(Host).filter(Host.c.bogomips<512).count()))
    stats['bogomips'].append(("between 512 and 1023",
                            session.query(Host).filter(and_(Host.c.bogomips>=512,
                                                    Host.c.bogomips<1024)).count()))
    stats['bogomips'].append(("between 1024 and 2047",
                            session.query(Host).filter(and_(Host.c.bogomips>=1024,
                                                    Host.c.bogomips<2048)).count()))
    stats['bogomips'].append(("between 2048 and 4000",
                            session.query(Host).filter(and_(Host.c.bogomips>=2048,
                                                    Host.c.bogomips<4000)).count()))
    stats['bogomips'].append(("more than 4000",
                            session.query(Host).filter(Host.c.system_memory>=4000).count()))


stats['languagetot'] = stats['total_hosts']

print 'number of cpus'
stats['num_cpus'] = session.query(NumCPUs).select()

print 'bogomips count'
stats['bogomips_total'] = session.query(Host).filter(Host.c.bogomips > 0).sum(Host.c.bogomips * Host.c.num_cpus)

print 'cpu speed total'
stats['cpu_speed_total'] = session.query(Host).filter(Host.c.cpu_speed > 0).sum(Host.c.cpu_speed * Host.c.num_cpus)

print 'cpus total'
stats['cpus_total'] = session.query(Host).sum(Host.c.num_cpus)

print 'registered devices'
stats['registered_devices'] = session.query(ComputerLogicalDevice).count()

if not  template_config['filesystem'] == [] :
    print 'filesystems'
    stats['filesystems'] = session.query(FileSys).select()
    stats['total_fs'] = session.query(FileSys).sum(FileSys.c.cnt)
    GB=1048576
    stats['combined_fs_size']=[]
    stats['combined_fs_size'].append(("less than 2GB",session.query(FileSystem).filter((FileSystem.c.f_fssize) <= (2*GB)  ) .count()))
    stats['combined_fs_size'].append(("Between 2GB and 80GB",
            session.query(FileSystem).filter(and_(FileSystem.c.f_fssize > (2*GB),
            FileSystem.c.f_fssize <= (80*GB))).count()))
    stats['combined_fs_size'].append(("Between 80GB and 200GB",
            session.query(FileSystem).filter(and_(FileSystem.c.f_fssize > (80*GB),
            FileSystem.c.f_fssize <= (200*GB))).count()))
    stats['combined_fs_size'].append(("Between 200GB and 400GB",
            session.query(FileSystem).filter(and_(FileSystem.c.f_fssize > (200*GB),
            FileSystem.c.f_fssize <= (400*GB))).count()))
    stats['combined_fs_size'].append(("Between 400GB and 800GB",
            session.query(FileSystem).filter(and_(FileSystem.c.f_fssize > (400*GB),
            FileSystem.c.f_fssize <= (800*GB))).count()))
    stats['combined_fs_size'].append(("Between 800GB and 1TB",
            session.query(FileSystem).filter(and_(FileSystem.c.f_fssize > (800*GB),
            FileSystem.c.f_fssize <= (1024*GB))).count()))
    stats['combined_fs_size'].append(("Between 1TB and 3TB",
            session.query(FileSystem).filter(and_(FileSystem.c.f_fssize > (1024*GB),
            FileSystem.c.f_fssize <= (3072*GB))).count()))
    stats['combined_fs_size'].append(("Over 3TB",session.query(FileSystem).filter((FileSystem.c.f_fssize) > (3072*GB)  ) .count()))



t=engine.load_template('hardware.templates.stats')
out_html=_process_output(dict(stat=stats, tabs=tabs,
                              total_hosts=total_hosts, 
                              getOSWikiLink=getOSWikiLink,
                              flot=flot,
                              template_config=template_config,
                              total_active_hosts=total_active_hosts),
                         template=t, format='html')

fname = "%s/stats.html" % (page_path)
f = open(fname, "w")
f.write(out_html)
f.close()

# Save some memory
del out_html
del stats

devices = {}
print 'total devices'
devices['total'] = session.query(HostLink).count()

print 'device type count'
devices['count'] = session.query(ComputerLogicalDevice).count()

print 'total hosts'
devices['total_hosts'] = session.query(Host).count()

print 'top 100 total list'
#devices['totalList'] = session.query(TotalList).select(limit=100)
devices['totalList'] = select([ComputerLogicalDevice.c.description, ComputerLogicalDevice.c.id, func.count(ComputerLogicalDevice.c.id).label('cnt')], HostLink.c.device_id == ComputerLogicalDevice.c.id).group_by(ComputerLogicalDevice.c.id).order_by(desc('cnt')).limit(10).execute().fetchall()

#print 'top 100 unique list'
#devices['uniqueList'] = session.query(UniqueList).select(limit=100)

print 'class list'
devices['classes'] = session.query(HardwareClass).select()


t=engine.load_template('hardware.templates.devices')

out_html = _process_output(dict(devices=devices, tabs=tabs,
                                total_hosts=total_hosts),
                           template=t, format='html')
fname = "%s/devices.html" % (page_path)
f = open(fname, "w")
f.write(out_html)
f.close()

# Save some memory
del devices
del out_html
