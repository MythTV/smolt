#!/usr/bin/python
# -*- coding: utf-8 -*-
__requires__ = "Turbogears[future]"
import pkg_resources
pkg_resources.require("TurboGears")


# Import without warnings on stderr
import sys
stderr_backup = sys.stderr
class DevNull:
    def write(self, data):
        pass
    def flush(self):
        pass


# BEGIN Import error silencer
sys.stderr = DevNull()
from turbogears.view import engines
sys.stderr = stderr_backup
# END Import error silencer


import turbogears.view
import turbogears.util as tg_util
from turbogears import view, database, errorhandling, config
from itertools import izip
from inspect import isclass
from turbogears import update_config, start_server

# BEGIN Import error silencer
sys.stderr = DevNull()
import cherrypy
sys.stderr = stderr_backup
# END Import error silencer


cherrypy.lowercase_api = True
from os.path import *
import time
from hardware.wiki import *
from turboflot import TurboFlot

WITHHELD_MAGIC_STRING = 'WITHHELD'
withheld_label = "withheld"

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


# BEGIN Import error silencer
sys.stderr = DevNull()
from hardware.model import *
sys.stderr = stderr_backup
# END Import error silencer


from hardware.hwdata import DeviceMap

#bind = metadata.bind
from turbogears.widgets import Tabber
tabs = Tabber()

# the path, where to store the generated pages
page_path = "hardware/static/stats"

turbogears.view.load_engines()
engine = engines.get('genshi', None)
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




right_now = date.today() - timedelta(days=90)
right_now = '%s-%s-%s' % (right_now.year, right_now.month, right_now.day)


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

def handle_withheld_elem(list, attrib_to_check, value_to_check_for):
    """finds the the withheld special entry,
        fixes it's label, and moves it to the end"""
    condition = lambda x: getattr(x, attrib_to_check) == value_to_check_for
    def modify(x):
        setattr(x, attrib_to_check, withheld_label)
        return x
    other_list = [e for e in list if not condition(e)]
    withheld_list = [modify(e) for e in list if condition(e)]
    return other_list + withheld_list
"""
stats = {}
# somehow this has to be first, cause it binds us to
# an sqlalchemy context
# total hosts is also defined below, one of these should be removed.
print '====================== total_hosts ======================'
stats['total_hosts'] = session.query(Host).count() + session.query(HostArchive).count()


class ByClass(object):
    def __init__(self):
        self.data = {}

    def fetch_data(self):
#        classes = session.query(HardwareClass).select()
        classes = session.query(HardwareClass).all()
        count = {}
        types = {}
        vendors = {}
        total_hosts = 0

        # We only want hosts that detected hardware (IE, hal was working properly)
        print 'Device: total_host with hardware'
        #total_hosts = select([func.count(func.distinct(host_links.c.host_link_id))])\
        #              .execute().fetchone()[0]
        total_hosts=stats['total_hosts']

        for cls in classes:
            type = cls.cls

            #devs = select([computer_logical_devices], computer_logical_devices.c.cls == type).alias("devs")
            devs = computer_logical_devices
            print 'Device: %s types' % type
#            Device=select([ComputerLogicalDevice.id, ComputerLogicalDevice.description,
#              ComputerLogicalDevice.bus, ComputerLogicalDevice.driver,
#              ComputerLogicalDevice.cls, ComputerLogicalDevice.date_added,
#              ComputerLogicalDevice.device_id, ComputerLogicalDevice.vendor_id,
#              ComputerLogicalDevice.subsys_device_id,
#              ComputerLogicalDevice.subsys_vendor_id],
#              ComputerLogicalDevice.cls==type).alias('d')
#            types = select([Device, func.count(HostLink.host_link_id.distinct()
#                    ).label('count')], Device.c.id==HostLink.device_id).group_by(Device.c.id)\
#                    .order_by(desc('count')).limit(100).execute().fetchall()
            types = select([ComputerLogicalDevice.id, ComputerLogicalDevice.description,
                ComputerLogicalDevice.bus, ComputerLogicalDevice.driver,
                ComputerLogicalDevice.cls, ComputerLogicalDevice.date_added,
                ComputerLogicalDevice.device_id, ComputerLogicalDevice.vendor_id,
                ComputerLogicalDevice.subsys_device_id,
                ComputerLogicalDevice.subsys_vendor_id, ComputerLogicalDevice.cls,
                func.count(HostLink.host_link_id.distinct()).label('count')],
                and_(ComputerLogicalDevice.cls==type, ComputerLogicalDevice.id==HostLink.device_id)).group_by(ComputerLogicalDevice.id).order_by(desc('count')).limit(100).execute().fetchall()

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
    for t in types:
        try:
            t.description = t.description.decode('latin1')
            pass
        except AttributeError:
            pass
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
if byclass_cache.data:
    del byclass_cache
    del out_html

stats = {}

print '====================== total_active_hosts ======================'
total_active_hosts = session.query(Host).filter(Host.last_modified > (date.today() - timedelta(days=90))).count()
if not total_active_hosts:
   total_active_hosts = 1

print '====================== total_hosts ======================'
stats['total_hosts'] = session.query(Host).count() + session.query(HostArchive).count()

total_hosts = stats['total_hosts']
flot = {}
# Arch calculation
if not  template_config['archs'] == [] :
    print '====================== archs ======================'
    session.bind = metadata.bind
    stats['archs'] = session.execute('''select count(platform), platform from host use index(platform) where host.last_modified > '%s' group by platform order by count(platform) desc;''' % right_now).fetchall()
#    stats['archs'] = handle_withheld_elem(
#            session.query(Arch).all(),
#            'platform', WITHHELD_MAGIC_STRING)
#    archs = []
#    counts = []
#    i = 0
#    for arch in stats['archs']:
#        archs.append([i + .5, arch.platform])
#        counts.append([i, arch.cnt])
#        i += 1
#    flot['archs'] = TurboFlot([
#        {   'data' : counts,
#            'bars' : { 'show' : True },
#            'label' : 'Archs', }],
#        {   'xaxis' : { 'ticks' : archs }, } )

print "====================== OS Stats ======================"
if not  template_config['os'] == [] :
    stats['os'] = handle_withheld_elem(
            session.query(OS).limit(30).all(),
            'os', WITHHELD_MAGIC_STRING)


print "====================== Runlevel stats ======================"
if not  template_config['runlevel'] == [] :
    stats['runlevel'] = handle_withheld_elem(
            session.query(Runlevel).all(),
            'runlevel', -1)


print "====================== Vendor stats ======================"
if not  template_config['vendors'] == [] :
    stats['vendors'] = handle_withheld_elem(
            session.query(Vendor).limit(100).all(),
            'vendor', WITHHELD_MAGIC_STRING)


print "====================== Model stats ======================"
if not  template_config['model'] == [] :
    stats['systems'] = handle_withheld_elem(
            session.query(System).limit(100).all(),
            'system', WITHHELD_MAGIC_STRING)

print "====================== CPU stats ======================"
stats['cpu_vendor'] = handle_withheld_elem(
        session.query(CPUVendor).limit(100).all(),
        'cpu_vendor', WITHHELD_MAGIC_STRING)

if not  template_config['kernel'] == [] :
    print "====================== Kernel stats ======================"
    stats['kernel_version'] = handle_withheld_elem(
            session.query(KernelVersion).limit(20).all(),
            'kernel_version', WITHHELD_MAGIC_STRING)

if not  template_config['formfactor'] == [] :
    print '====================== Formfactor stats ======================'
    stats['formfactor'] = handle_withheld_elem(
            session.query(FormFactor).limit(8).all(),
            'formfactor', WITHHELD_MAGIC_STRING)

if not  template_config['lang'] == [] :
    print '====================== language stats ======================'
    stats['language'] = handle_withheld_elem(
            session.query(Language).all(),
            'language', WITHHELD_MAGIC_STRING)

if not  template_config['selinux'] == [] :
    print '====================== selinux stats ======================'
    stats['selinux_enabled'] = handle_withheld_elem(
            session.query(SelinuxEnabled).all(),
            'enabled', -1)

    stats['selinux_enforce'] = handle_withheld_elem(
            session.query(SelinuxEnforced).all(),
            'enforce', WITHHELD_MAGIC_STRING)

    stats['selinux_policy'] = handle_withheld_elem(
            session.query(SelinuxPolicy).all(),
            'policy', WITHHELD_MAGIC_STRING)

now = date.today() - timedelta(days=90)

if not  template_config['ram'] == [] :
    print '====================== memory stats ======================'
    stats['sys_mem'] = []
    stats['sys_mem'].append(("less than 256mb",
                            session.query(Host).filter(and_(
                                                    Host.system_memory!=0,
                                                    Host.system_memory<256,
                                                    Host.last_modified > (now))).count()))
    stats['sys_mem'].append(("between 256mb and 512mb",
                            session.query(Host).filter(and_(
                                                    Host.system_memory>=256,
                                                    Host.system_memory<512,
                                                    Host.last_modified > (now))).count()))
    stats['sys_mem'].append(("between 512mb and 1023mb",
                            session.query(Host).filter(and_(
                                                    Host.system_memory>=512,
                                                    Host.system_memory<1024,
                                                    Host.last_modified > (now))).count()))
    stats['sys_mem'].append(("between 1024mb and 2047mb",
                            session.query(Host).filter(and_(
                                                    Host.system_memory>=1024,
                                                    Host.system_memory<2048,
                                                    Host.last_modified > (now))).count()))
    stats['sys_mem'].append(("between 2048mb and 4095mb",
                            session.query(Host).filter(and_(
                                                    Host.system_memory>=2048,
                                                    Host.system_memory<4096,
                                                    Host.last_modified > (now))).count()))
    stats['sys_mem'].append(("between 4096mb and 8191mb",
                            session.query(Host).filter(and_(
                                                    Host.system_memory>=4096,
                                                    Host.system_memory<8191,
                                                    Host.last_modified > (now))).count()))
    stats['sys_mem'].append(("between 8192mb and 16383mb",
                            session.query(Host).filter(and_(
                                                    Host.system_memory>=8192,
                                                    Host.system_memory<16383,
                                                    Host.last_modified > (now))).count()))
    stats['sys_mem'].append(("more than 16384mb",
                            session.query(Host).filter(and_(
                                                    Host.system_memory>=16384,
                                                    Host.last_modified > (now))).count()))
    stats['sys_mem'].append((withheld_label,
                            session.query(Host).filter(and_(
                                                    Host.system_memory==0,
                                                    Host.last_modified > (now))).count()))

if not  template_config['swap'] == [] :
    print '====================== swap stats ======================'
    stats['swap_mem'] = []
    stats['swap_mem'].append(("less than 512mb",
                            session.query(Host).filter(and_(
                                                    Host.system_swap!=0,
                                                    Host.system_swap<512,
                                                    Host.last_modified > (now))).count()))
    stats['swap_mem'].append(("between 512mb and 1027mb",
                            session.query(Host).filter(and_(
                                                    Host.system_swap>=512,
                                                    Host.system_swap<1024,
                                                    Host.last_modified > (now))).count()))
    stats['swap_mem'].append(("between 1024mb and 2047mb",
                            session.query(Host).filter(and_(
                                                    Host.system_swap>=1024,
                                                    Host.system_swap<2048,
                                                    Host.last_modified > (now))).count()))
    stats['swap_mem'].append(("between 2048mb and 4095",
                            session.query(Host).filter(and_(
                                                    Host.system_swap>=2048,
                                                    Host.system_swap<4095,
                                                    Host.last_modified > (now))).count()))
    stats['swap_mem'].append(("between 4096mb and 8191",
                            session.query(Host).filter(and_(
                                                    Host.system_swap>=4096,
                                                    Host.system_swap<8191,
                                                    Host.last_modified > (now))).count()))
    stats['swap_mem'].append(("more than 8192",
                            session.query(Host).filter(and_(
                                                    Host.system_swap>=8192,
                                                    Host.last_modified > (now))).count()))
    stats['swap_mem'].append((withheld_label,
                            session.query(Host).filter(and_(
                                                    Host.system_swap==0,
                                                    Host.last_modified > (now))).count()))

#cpu tab
if not  template_config['cpu'] == [] :
    print '====================== cpu stats ======================'
    stats['cpu_speed'] = []
    stats['cpu_speed'].append(("less than 512mhz",
                            session.query(Host).filter(and_(
                                                    Host.cpu_speed!=0,
                                                    Host.cpu_speed<512,
                                                    Host.last_modified > (now))).count()))
    stats['cpu_speed'].append(("between 512mhz and 1023mhz",
                            session.query(Host).filter(and_(
                                                    Host.cpu_speed>=512,
                                                    Host.cpu_speed<1024,
                                                    Host.last_modified > (now))).count()))
    stats['cpu_speed'].append(("between 1024mhz and 2047mhz",
                            session.query(Host).filter(and_(
                                                    Host.cpu_speed>=1024,
                                                    Host.cpu_speed<2048,
                                                    Host.last_modified > (now))).count()))
    stats['cpu_speed'].append(("more than 2048mhz",
                            session.query(Host).filter(and_(
                                                    Host.cpu_speed>=2048,
                                                    Host.last_modified > (now))).count()))
    stats['cpu_speed'].append((withheld_label,
                            session.query(Host).filter(and_(
                                                    Host.cpu_speed==0,
                                                    Host.last_modified > (now))).count()))

    stats['bogomips'] = []
    stats['bogomips'].append(("less than 512",
                            session.query(Host).filter(and_(
                                                    Host.bogomips!=0,
                                                    Host.bogomips<512,
                                                    Host.last_modified > (now))).count()))
    stats['bogomips'].append(("between 512 and 1023",
                            session.query(Host).filter(and_(
                                                    Host.bogomips>=512,
                                                    Host.bogomips<1024,
                                                    Host.last_modified > (now))).count()))
    stats['bogomips'].append(("between 1024 and 2047",
                            session.query(Host).filter(and_(
                                                    Host.bogomips>=1024,
                                                    Host.bogomips<2048,
                                                    Host.last_modified > (now))).count()))
    stats['bogomips'].append(("between 2048 and 4000",
                            session.query(Host).filter(and_(
                                                    Host.bogomips>=2048,
                                                    Host.bogomips<4000,
                                                    Host.last_modified > (now))).count()))
    stats['bogomips'].append(("more than 4000",
                            session.query(Host).filter(and_(
                                                    Host.bogomips>=4000,
                                                    Host.last_modified > (now))).count()))
    stats['bogomips'].append((withheld_label,
                            session.query(Host).filter(and_(
                                                    Host.bogomips==0,
                                                    Host.last_modified > (now))).count()))



#    stats['bogomips'].append((withheld_label,
#                            session.query(Host).filter(and_(
#                                                    Host.bogomips==0,
#                                                    Host.last_modified > (now))).count()))

stats['languagetot'] = stats['total_hosts']

print 'number of cpus'
stats['num_cpus'] = handle_withheld_elem(
        session.query(NumCPUs).all(),
        'num_cpus', 0)


print '====================== bogomips count ======================'
conn = select([func.sum(Host.bogomips * Host.num_cpus)]).where(Host.bogomips > 0).limit(1).execute()
stats['bogomips_total'] = conn.fetchone()
conn.close()

print '====================== cpu speed total ======================'
conn = select([func.sum(Host.cpu_speed * Host.num_cpus)]).where(Host.cpu_speed > 0).limit(1).execute()
stats['cpu_speed_total'] = conn.fetchone()
conn.close()

print '====================== cpus total ======================'
conn = select([func.sum(Host.num_cpus)]).limit(1).execute()
stats['cpus_total'] = conn.fetchone()
conn.close()

print '====================== registered devices ======================'
stats['registered_devices'] = session.query(ComputerLogicalDevice).count()

if not  template_config['filesystem'] == [] :
    print '====================== filesystems ======================'
    #stats['filesystems'] = session.query(FileSys).all()
    # SELECT file_systems.fs_type, count(file_systems.fs_type) AS cnt FROM file_systems, host use index(last_modified_join) WHERE file_systems.host_id = host.id AND host.last_modified > '2009-06-11' GROUP BY file_systems.fs_type ORDER BY count(file_systems.fs_type) DESC;
    session.bind = metadata.bind
    stats['filesystems'] = session.execute('''SELECT file_systems.fs_type, count(file_systems.fs_type) AS cnt FROM file_systems, host use index(last_modified_join) WHERE file_systems.host_id = host.id AND host.last_modified > '%s' GROUP BY file_systems.fs_type ORDER BY count(file_systems.fs_type) DESC;''' % right_now).fetchall()
    stats['total_fs'] = session.query(FileSys).count()
    if not stats['total_fs']:
        stats['total_fs'] = 1
    GB=1048576
    stats['combined_fs_size']=[]
    stats['combined_fs_size'].append(("less than 2GB",session.query(FileSystem).filter(and_(FileSystem.f_fssize!=0, FileSystem.f_fssize <= (2*GB))).count()))
    stats['combined_fs_size'].append(("Between 2GB and 80GB",
            session.query(FileSystem).filter(and_(FileSystem.f_fssize!=0, FileSystem.f_fssize > (2*GB),
            FileSystem.f_fssize <= (80*GB))).count()))
    stats['combined_fs_size'].append(("Between 80GB and 200GB",
            session.query(FileSystem).filter(and_(FileSystem.f_fssize!=0, FileSystem.f_fssize > (80*GB),
            FileSystem.f_fssize <= (200*GB))).count()))
    stats['combined_fs_size'].append(("Between 200GB and 400GB",
            session.query(FileSystem).filter(and_(FileSystem.f_fssize!=0, FileSystem.f_fssize > (200*GB),
            FileSystem.f_fssize <= (400*GB))).count()))
    stats['combined_fs_size'].append(("Between 400GB and 800GB",
            session.query(FileSystem).filter(and_(FileSystem.f_fssize!=0, FileSystem.f_fssize > (400*GB),
            FileSystem.f_fssize <= (800*GB))).count()))
    stats['combined_fs_size'].append(("Between 800GB and 1TB",
            session.query(FileSystem).filter(and_(FileSystem.f_fssize!=0, FileSystem.f_fssize > (800*GB),
            FileSystem.f_fssize <= (1024*GB))).count()))
    stats['combined_fs_size'].append(("Between 1TB and 3TB",
            session.query(FileSystem).filter(and_(FileSystem.f_fssize!=0, FileSystem.f_fssize > (1024*GB),
            FileSystem.f_fssize <= (3072*GB))).count()))
    stats['combined_fs_size'].append(("Over 3TB",session.query(FileSystem).filter(and_(FileSystem.f_fssize!=0, (FileSystem.f_fssize) > (3072*GB)  )) .count()))
    stats['combined_fs_size'].append((withheld_label,session.query(FileSystem).filter(FileSystem.f_fssize==0) .count()))


#myth stuff
#---------------
template_config['smoon.myth_support'] = ''
if config.get("smoon.myth_support"):
    template_config['smoon.myth_support'] = 'YES'
    template_config['myth_role']=config.get("stats_template.myth_role", [])
    template_config['myth_remote']=config.get("stats_template.myth_remote", [])
    template_config['myth_theme']=config.get("stats_template.myth_theme", [])
    template_config['myth_plugins']=config.get("stats_template.myth_theme", [])
    template_config['myth_tuner']=config.get("stats_template.myth_theme", [])

    print "====================== Myth Role ======================"
    if not  template_config['myth_role'] == [] :
        stats['myth_role'] = handle_withheld_elem(
                session.query(MythRole).limit(30).all(),
                'myth_role', WITHHELD_MAGIC_STRING)

    print "====================== Myth Remote ======================"
    if not  template_config['myth_remote'] == [] :
        stats['myth_remote'] = handle_withheld_elem(
                session.query(MythRemote).limit(30).all(),
                'myth_remote', WITHHELD_MAGIC_STRING)

    print "====================== Myth theme ======================"
    if not  template_config['myth_theme'] == [] :
        stats['myth_theme'] = handle_withheld_elem(
                session.query(MythTheme).limit(30).all(),
                'myth_theme', WITHHELD_MAGIC_STRING)

    print "====================== Myth plugins ======================"
    if not  template_config['myth_plugins'] == [] :
        temp_list = []
        stats['myth_plugins']=[]
        plugin_count = {}
        temp_list = session.execute('''SELECT myth_plugins from host where host.last_modified > '%s' and not myth_plugins = ''  ;''' %
        right_now).fetchall()
        #print temp_list
        #sys.exit(2)
        for i in temp_list:
            #retrieve the first record in the list
            y = i[0]
            split_plugins = y.split(',')
            for plugin in split_plugins:
                if plugin in plugin_count:
                    plugin_count[plugin] = plugin_count[plugin] + 1
                else:
                    plugin_count[plugin] = 1

        stats['myth_plugins'] = plugin_count
        del temp_list
        del plugin_count

    print "====================== Myth Tuners ======================"
    if not  template_config['myth_tuner'] == [] :

        stats['myth_tuner']=[]
        stats['myth_tuner'].append(("One Tuner",
                            session.query(Host).filter(and_(
                                                    Host.myth_tuner!=0,
                                                    Host.myth_tuner==1,
                                                    Host.last_modified > (now))).count()))

        stats['myth_tuner'].append(("Two Tuners",
                            session.query(Host).filter(and_(
                                                    Host.myth_tuner!=0,
                                                    Host.myth_tuner==2,
                                                    Host.last_modified > (now))).count()))
        stats['myth_tuner'].append(("Three Tuners",
                            session.query(Host).filter(and_(
                                                    Host.myth_tuner!=0,
                                                    Host.myth_tuner==3,
                                                    Host.last_modified > (now))).count()))
        stats['myth_tuner'].append(("Four Tuners",
                            session.query(Host).filter(and_(
                                                    Host.myth_tuner!=0,
                                                    Host.myth_tuner==4,
                                                    Host.last_modified > (now))).count()))
        stats['myth_tuner'].append(("Five Tuners",
                            session.query(Host).filter(and_(
                                                    Host.myth_tuner!=0,
                                                    Host.myth_tuner==5,
                                                    Host.last_modified > (now))).count()))
        stats['myth_tuner'].append(("Six Tuners",
                            session.query(Host).filter(and_(
                                                    Host.myth_tuner!=0,
                                                    Host.myth_tuner==6,
                                                    Host.last_modified > (now))).count()))
        stats['myth_tuner'].append(("Seven Tuners",
                            session.query(Host).filter(and_(
                                                    Host.myth_tuner!=0,
                                                    Host.myth_tuner==7,
                                                    Host.last_modified > (now))).count()))
        stats['myth_tuner'].append(("Eight Tuners",
                            session.query(Host).filter(and_(
                                                    Host.myth_tuner!=0,
                                                    Host.myth_tuner==8,
                                                    Host.last_modified > (now))).count()))
        stats['myth_tuner'].append(("Nine Tuners",
                            session.query(Host).filter(and_(
                                                    Host.myth_tuner!=0,
                                                    Host.myth_tuner==9,
                                                    Host.last_modified > (now))).count()))
        stats['myth_tuner'].append(("Ten Tuners",
                            session.query(Host).filter(and_(
                                                    Host.myth_tuner!=0,
                                                    Host.myth_tuner==10,
                                                    Host.last_modified > (now))).count()))
        stats['myth_tuner'].append(("More Then Ten Tuners",
                            session.query(Host).filter(and_(
                                                    Host.myth_tuner!=0,
                                                    Host.myth_tuner>=10,
                                                    Host.last_modified > (now))).count()))

#------------------





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
"""
def do_distro_specific_renderinging():
    import gentooanalysis
    import datetime
    gentoo_data_tree = gentooanalysis.gentoo_data_tree(session)
    t = engine.load_template('hardware.templates.gentoo')
    out_html = _process_output(dict(data=gentoo_data_tree), template=t, format='html')
    fname = "%s/gentoo.html" % (page_path)
    f = open(fname, "w")
    f.write(out_html)
    f.close()

    t = engine.load_template('hardware.templates.gentoo_zero_installs_packages')
    out_txt = _process_output(dict(data=gentoo_data_tree), template=t, format='html')
    # Kill HTML intro and outro. TODO Resolve dirty hack
    out_txt = '\n'.join(e for e in out_txt.split('\n') if not e.startswith('<'))
    fname = "%s/gentoo_zero_installs_packages.txt" % (page_path)
    f = open(fname, "w")
    f.write(out_txt)
    f.close()

do_distro_specific_renderinging()
"""
# Save some memory
del out_html
del stats

devices = {}
print '====================== total devices ======================'
devices['total'] = session.query(HostLink).count()

print '====================== device type count ======================'
devices['count'] = session.query(ComputerLogicalDevice).count()

print '====================== total hosts ======================'
devices['total_hosts'] = session.query(Host).count()

print '====================== top 100 total list ======================'
#devices['totalList'] = session.query(TotalList).select(limit=100)
devices['totalList'] = select([ComputerLogicalDevice.description, ComputerLogicalDevice.id, func.count(ComputerLogicalDevice.id).label('cnt')], HostLink.device_id == ComputerLogicalDevice.id).group_by(ComputerLogicalDevice.id).order_by(desc('cnt')).limit(10).execute().fetchall()

#print 'top 100 unique list'
#devices['uniqueList'] = session.query(UniqueList).select(limit=100)

print '====================== class list ======================'
devices['classes'] = session.query(HardwareClass).all()


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
"""