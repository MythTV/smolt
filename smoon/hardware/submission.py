# smolt - Fedora hardware profiler
#
# Copyright (C) 2007 Mike McGrath
# Copyright (C) 2009 Sebastian Pipping <sebastian@pipping.org>
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

import logging
import simplejson
from sqlalchemy.exceptions import InvalidRequestError, OperationalError
from datetime import datetime
from hardware.model.model import *
from hardware.uuid import generate_uuid

def handle_submission(session, uuid, host):
    logging.info('Processing hardware UUID %s' % uuid)
    host_dict = simplejson.loads(host)
    try:
        host_sql = session.query(Host).filter_by(uuid=uuid).one()
    except InvalidRequestError:
        host_sql = Host()
        host_sql.uuid = host_dict["uuid"]
        host_sql.pub_uuid = generate_uuid(public=True)
    except OperationalError:
        host_sql = Host()
        host_sql.uuid = host_dict["uuid"]
        host_sql.pub_uuid = generate_uuid(public=True)
    # Fix lsb vs release error in F11.
    if host_dict['os'] == 'Fedora 11 Leonidas':
        host_sql.os = 'Fedora release 11 (Leonidas)'
    else:
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
    host_sql.last_modified = datetime.now()
    if host_sql.formfactor is None:
        host_sql.formfactor = 'unknown'
    host_sql.selinux_enabled = host_dict['selinux_enabled']
    try:
        host_sql.selinux_policy = host_dict['selinux_policy']
    except KeyError:
        host_sql.selinux_policy = 'Unknown'
    try:
        host_sql.cpu_stepping = host_dict['cpu_stepping']
        host_sql.cpu_family = host_dict['cpu_family']
        host_sql.cpu_model_num = host_dict['cpu_model_num']
    except KeyError:
        host_sql.cpu_stepping = host_sql.cpu_family = host_sql.cpu_model_num = None
        host_sql.selinux_enforce = host_dict['selinux_enforce']

#    try:
#            host_sql.myth_systemrole = host_dict['myth_systemrole']
#    except KeyError:
#            host_sql.myth_systemrole = 'Unknown'
#    try:
#            host_sql.mythremote = host_dict['mythremote']
#    except KeyError:
#            host_sql.mythremote = 'Unknown'
#    try:
#            host_sql.myththeme = host_dict['myththeme']
#     except KeyError:
#            host_sql.myththeme = 'Unknown'

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
            device_sql = session.query(ComputerLogicalDevice)\
                .filter_by(device_id=device_id,
                            vendor_id=vendor_id,
                            subsys_vendor_id=subsys_vendor_id,
                            subsys_device_id=subsys_device_id,
                            description=description).one()
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
            device_sql.date_added = datetime.today()

            d = device_sql

            try:
                class_sql = session.query(HardwareClass).filter_by(cls=cls).one()
                device_sql.hardware_class = class_sql
            except InvalidRequestError:
                class_sql = HardwareClass()
                class_sql.cls = cls
                class_sql.class_description = "Fill me in!"
                device_sql.hardware_class = class_sql
                session.flush()

            session.flush()

            host_link = HostLink()
            host_link.host = host_sql
            host_link.device = device_sql

    for device_sql_id in orig_devices:
        bad_host_link = session.query(HostLink)\
        .filter(and_(HostLink.device_id==device_sql_id,
        HostLink.host_link_id==host_sql.id))
        if bad_host_link and bad_host_link > 0:
            session.delete(bad_host_link[0])
    session.flush()

    map(session.delete, host_sql.file_systems)
    def add_fs(fs_dict):
        new_fs = FileSystem()
        new_fs.mnt_pnt = fs_dict['mnt_pnt']
        new_fs.fs_type = fs_dict['fs_type']
        new_fs.f_favail = fs_dict['f_favail']
        new_fs.f_bsize = fs_dict['f_bsize']
        new_fs.f_frsize = fs_dict['f_frsize']
        new_fs.f_blocks = fs_dict['f_blocks']
        new_fs.f_bfree = fs_dict['f_bfree']
        new_fs.f_bavail = fs_dict['f_bavail']
        new_fs.f_files = fs_dict['f_files']
        new_fs.f_ffree = fs_dict['f_ffree']
        new_fs.f_fssize = (fs_dict['f_blocks'] * fs_dict['f_bsize'] ) / 1024
        new_fs.host = host_sql
    try:
        map(add_fs, host_dict['fss'])
    except:
        pass

    return dict(pub_uuid=host_sql.pub_uuid)
