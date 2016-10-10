#!/usr/bin/env python
# -*- coding: utf-8 -*-
# smolt - Fedora hardware profiler
#
# Copyright (C) 2007 Mike McGrath
# Copyright (C) 2010 Sebastian Pipping <sebastian@pipping.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301, USA.

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
from hardware.turboflot import TurboFlot
from hardware.featureset import init, config_filename, at_final_server
from reportutils import _process_output
from turbogears.database import session
from hardware.featureset import this_is, MYTH_TV

WITHHELD_MAGIC_STRING = 'WITHHELD'
withheld_label = "withheld"

_cfg_filename = None
if len(sys.argv) > 1:
    _cfg_filename = sys.argv[1]

init(_cfg_filename)
update_config(configfile=config_filename(),modulename="hardware.config")

from sqlalchemy import *

from hardware.model import *
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
    out_html = _process_output(engine, dict(types=types, type=type,
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
    # FIXME Extend our alchemy model to allow "use index(platform)"
    if at_final_server():
        stats['archs'] = session.execute('''select count(platform), platform from host use index(platform) where host.last_modified > '%s' group by platform order by count(platform) desc;''' % right_now).fetchall()
    else:
        stats['archs'] = session.execute('''select count(platform), platform from host                     where host.last_modified > '%s' group by platform order by count(platform) desc;''' % right_now).fetchall()
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
            session.query(OS).limit(45).all(),
            'os', WITHHELD_MAGIC_STRING)


    class os_stat:
        def __init__(self, bucket, tbl_num):
            self.bucket = bucket
            self.os_dict = {}
            self.total_count = 0
            self.tbl_num = tbl_num
            pass


        def set_tbl(self, tbl_num):
            self.tbl_num = tbl_num

        def add_os(self, os , count):
            self.os_dict[os] = count
            #update total hosts
            self.total_count = self.total_count + count

        def get_os_list(self):
            os_list = self.os_dict.keys()
            return os_list

        def get_count(self, os):
            count = self.os_dict[os]
            return count

        def get_total(self):
            return self.total_count

        def get_bucket(self):
            return self.bucket

        def get_tbl(self):
            return self.tbl_num

        def sort_os(self):
            self.sorted_os = sorted(self.os_dict, key=self.os_dict.get, reverse=True)

        def get_sorted_os(self):
            self.sort_os()
            return self.sorted_os




    #break down the OS by major distros
    os_search_list = {}
    os_search_list['redhat']  = [ 'fedora' , 'centos' , 'mythdora', 'redhat' ]
    os_search_list['suse']    = [ 'sles' , 'opensuse' , 'suse' ]
    os_search_list['ubuntu']  = [ 'ubuntu' ]
    os_search_list['linhes']   = [ 'linhes' ]
    os_search_list['debian']  = [ 'debian' ]
    os_search_list['linuxmint'] = [ 'linuxmint' ]
    os_search_list['raspbian'] = [ 'raspbian' ]

    os_stats_dict = { 'redhat':os_stat('RedHat',2) ,
                      'suse' : os_stat('SuSE',3) ,
                      'ubuntu' : os_stat('Ubuntu',4) ,
                      'linhes' : os_stat('LinHES',5) ,
                      'debian' : os_stat('Debian',6) ,
                      'other' : os_stat('Other',7) ,
                      'linuxmint' : os_stat('LinuxMint',8) ,
                      'raspbian' : os_stat('Raspbian', 9) }

    os_stats_sort_list = []

    # populate each bucket with it's OS
    for i in stats['os']:
        found = False
        for k,v in os_search_list.iteritems():
            for check_os in v:
                if check_os in i.os.lower():
                    bucket = k
                    found = True
                    break
                else :
                    bucket = 'other'
            #if found is true break out of the os_search_list loop
            if found == True :
                break
            else:
                continue

    #add the OS to the dict
        osbucket_d = os_stats_dict[bucket]
        osbucket_d.add_os(i.os,i.cnt)

    #this sorting is needed to make the html output look nice
    # create a list of buckets & total
    os_list=[]
    for k,v in os_stats_dict.iteritems():
        temp_tuple=(k,v.get_total())
        os_list.append(temp_tuple)

    #sort the list by total
    sort_list = sorted(os_list, key=lambda x: x[1] , reverse=True)
    #create list of os_stat objects
    for i in sort_list:
        os_stats_sort_list.append(os_stats_dict[i[0]] )
    stats['os_stat'] = os_stats_sort_list


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


def none_to_zero(iterable):
    """
    Makes a copy of an iterable with all <None>s replaced by 0
    """
    return ((0 if e is None else e) for e in iterable)


print '====================== bogomips count ======================'
conn = select([func.sum(Host.bogomips * Host.num_cpus)]).where(Host.bogomips > 0).limit(1).execute()
stats['bogomips_total'] = none_to_zero(conn.fetchone())
conn.close()

print '====================== cpu speed total ======================'
conn = select([func.sum(Host.cpu_speed * Host.num_cpus)]).where(Host.cpu_speed > 0).limit(1).execute()
stats['cpu_speed_total'] = none_to_zero(conn.fetchone())
conn.close()

print '====================== cpus total ======================'
conn = select([func.sum(Host.num_cpus)]).limit(1).execute()
stats['cpus_total'] = none_to_zero(conn.fetchone())
conn.close()

print '====================== registered devices ======================'
stats['registered_devices'] = session.query(ComputerLogicalDevice).count()

if not  template_config['filesystem'] == [] :
    print '====================== filesystems ======================'
    #stats['filesystems'] = session.query(FileSys).all()
    # SELECT file_systems.fs_type, count(file_systems.fs_type) AS cnt FROM file_systems, host use index(last_modified_join) WHERE file_systems.host_id = host.id AND host.last_modified > '2009-06-11' GROUP BY file_systems.fs_type ORDER BY count(file_systems.fs_type) DESC;
    session.bind = metadata.bind
    # FIXME Extend our alchemy model to allow "use index(last_modified_join)"
    if at_final_server():
        stats['filesystems'] = session.execute('''SELECT file_systems.fs_type, count(file_systems.fs_type) AS cnt FROM file_systems, host use index(last_modified_join) WHERE file_systems.host_id = host.id AND host.last_modified > '%s' GROUP BY file_systems.fs_type ORDER BY count(file_systems.fs_type) DESC;''' % right_now).fetchall()
    else:
        stats['filesystems'] = session.execute('''SELECT file_systems.fs_type, count(file_systems.fs_type) AS cnt FROM file_systems, host                              WHERE file_systems.host_id = host.id AND host.last_modified > '%s' GROUP BY file_systems.fs_type ORDER BY count(file_systems.fs_type) DESC;''' % right_now).fetchall()
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


if this_is(MYTH_TV):
    template_config['smoon.myth_support'] = True
    from render_stat_mythtv import render_mythtv
    stats = render_mythtv(stats)
else:
    template_config['smoon.myth_support'] = False

t=engine.load_template('hardware.templates.stats')
out_html=_process_output(engine, dict(stat=stats, tabs=tabs,
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

out_html = _process_output(engine, dict(devices=devices, tabs=tabs,
                                total_hosts=total_hosts),
                           template=t, format='html')
fname = "%s/devices.html" % (page_path)
f = open(fname, "w")
f.write(out_html)
f.close()

# Save some memory
del devices
del out_html
