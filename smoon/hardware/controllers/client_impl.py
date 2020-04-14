# -*- coding: utf-8 -*-
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

from urllib import quote
import copy
from datetime import datetime
import logging
import simplejson

from sqlalchemy.exc import InvalidRequestError, OperationalError
from turbogears.database import session

from hardware.hwdata import DeviceMap
from hardware.model import BatchJob, Host
from hardware.wiki import getDeviceWikiLink, getHostWikiLink, getOSWikiLink
from hardware.ratingwidget import SingleRatingWidget
from hardware.uuid import generate_uuid
import hardware.compat as compat
from hardware.model.model import *

from hardware.controllers.client import request_format


def _fix_vendor(vendor):
    rc = vendor
    if vendor.startswith('Dell'):
        rc = 'Dell, Inc.'
    return rc


class ClientImplementation(object):
    def __init__(self, smolt_protocol, token):
        self.smolt_protocol = smolt_protocol
        self.token = token

    def data_for_next_hop(self, host_dict):
        return copy.copy(host_dict)  # TODO

    def update_pub_uuid(self, uuid, pub_uuid):
        host_sql = session.query(Host).filter_by(uuid=uuid).one()
        host_sql.pub_uuid = pub_uuid
        session.flush()

    def show(self, uuid, UUID, admin):
        if UUID:
            uuid = UUID
        try:
            uuid = u'%s' % uuid.strip()
            uuid = uuid.encode('utf8')
        except:
            raise ValueError("Critical: Unicode Issue - Tell Mike!")

        try:
            host_object = session.query(Host).filter_by(pub_uuid=uuid).one()
        except:
            try:
                host_object = session.query(Host).selectone_by(uuid=uuid)
                raise ValueError("Critical: New versions of smolt use a public UUID.  Yours is: %s" % host_object.pub_uuid)
            except InvalidRequestError:
                raise ValueError("Critical: UUID Not Found - %s" % uuid)

        if admin:
            admin = self.token.check_admin_token(admin, host_object.uuid)

        devices = {}
        ven = DeviceMap('pci')

        for dev in host_object.devices:
            #session.refresh(dev)
            device = dev.device
            if not device.vendor_id and not device.device_id:
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
                                            description = quote(device.description).replace('/', '%2F')
                                            )

        devices = devices.values()
        devices.sort(key=lambda x: x.get('cls'))

        if request_format() == 'json':
          host_object['uuid'] = None
          return dict(host_object=host_object, devices=devices)

        return dict(host_object = host_object,
                    host_link = getHostWikiLink(host_object),
                    devices=devices,
                    ratingwidget=SingleRatingWidget(),
                    getOSWikiLink=getOSWikiLink,
                    admin=admin
                    )

    def show_all(self, uuid, admin):
        try:
            uuid = u'%s' % uuid.strip()
            uuid = uuid.encode('utf8')
        except:
            raise ValueError("Critical: Unicode Issue - Tell Mike!")
        try:
            host_object = session.query(Host).filter_by(pub_uuid=uuid).one()
        except:
            raise ValueError("Critical: UUID Not Found - %s" % uuid)
        if admin:
            admin = self.token.check_admin_token(admin, host_object.uuid)

        devices = {}
        for dev in host_object.devices:
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
                    getOSWikiLink=getOSWikiLink,
                    admin=admin
                    )

    def delete(self, uuid):
        # TODO also search and clean batch queue?
        try:
            host = session.query(Host).filter_by(uuid=uuid).one()
        except:
            raise ValueError("Critical: UUID does not exist %s " % uuid)
        try:
            session.delete(host)
            session.flush()
        except:
            raise ValueError("Critical: Could not delete UUID - Please contact the smolt development team")
        raise ValueError('Success: UUID Removed')

    def host_rating(self, vendor, system):
        q = session.query(Host).filter_by(vendor=vendor, system=system)
        q = compat.add_column(q, func.count(Host.rating).label('count')).group_by(Host.rating)

        ratings = {}
        for rate in q:
            ratings[rate[0].rating] = rate[1]
        return dict(ratings=ratings)

    def regenerate_pub_uuid(self, uuid):
        try:
            uuid = u'%s' % uuid.strip()
            uuid = uuid.encode('utf8')
        except:
            raise ValueError("Critical: Unicode Issue - Tell Mike!")

        try:
            host_object = session.query(Host).selectone_by(uuid=uuid)
        except:
            raise ValueError("Critical: UUID Not Found - %s" % uuid)

        try:
            pub_uuid = file('/proc/sys/kernel/random/uuid').read().strip()
            pub_uuid = "pub_" + pub_uuid
        except IOError:
            raise UUIDError("Cannot generate UUID")
        host_object.pub_uuid = pub_uuid
        session.flush()
        return dict(pub_uuid=pub_uuid)

    def _run_add_json_checks(self, uuid, host, token, smolt_protocol):
        if smolt_protocol < self.smolt_protocol:
            raise ValueError("Critical: Outdated smolt client.  Please upgrade.")
        if smolt_protocol > self.smolt_protocol:
            raise ValueError("Woah there marty mcfly, you got to go back to 1955!")

        self.token.check_token(token, uuid)

    def add_json_plus_pub_uuid(self, uuid, pub_uuid, host, token, smolt_protocol):
        self._run_add_json_checks(uuid, host, token, smolt_protocol)
        res = self.handle_submission(uuid, pub_uuid, host)
        log_entry = BatchJob(host, uuid, added=True)
        session.add(log_entry)
        session.flush()
        return res

    def rate_object(self, **kwargs):
        #log.info('args = %s' % str(args))
        #log.info('kwargs = %s' % str(kwargs))
        id = kwargs.get("ratingID")
        rating = kwargs.get("value")
        print "ID: %s" % id
        print "RATING: %s" % rating
        if id.startswith("Host"):
            sep = id.find("@")
            if sep == -1:
                host_id = id[4:]
                host = session.query(Host).filter_by(uuid=host_id).one()
                host.rating = int(rating)
                session.flush()
                return dict()

            host_id = id[4:sep]
            id = id[sep+1:]
            if id.startswith("Device"):
                device_id = int(id[6:])
                host = session.query(Host).filter_by(uuid=host_id).one()
                for device in host.devices:
                    if device.device_id == device_id:
                        device.rating = int(rating)
                        session.flush([host, device])
                        return dict()
        return dict()

    def batch_add_json(self, uuid, host, token, smolt_protocol):
        self._run_add_json_checks(uuid, host, token, smolt_protocol)
        job = BatchJob(host, uuid, added=False)
        session.add(job)
        session.flush()
        return dict()

    def pub_uuid(self, uuid):
        pub_uuid=select([Host.pub_uuid], Host.uuid==uuid).execute().fetchone()[0]
        return dict(pub_uuid=pub_uuid)

    def extend_host_sql_hook(self, host_sql, host_dict):
        return host_sql  # See subclasses

    def handle_submission(self, uuid, pub_uuid, host):
        logging.info('Processing hardware UUID %s' % uuid)
        host_dict = simplejson.loads(host)
        try:
            host_sql = session.query(Host).filter_by(uuid=uuid).one()
        except InvalidRequestError:
            host_sql = Host()
            host_sql.uuid = host_dict["uuid"]
            if pub_uuid:
                host_sql.pub_uuid = pub_uuid
            else:
                host_sql.pub_uuid = generate_uuid(public=True)
        except OperationalError:
            host_sql = Host()
            host_sql.uuid = host_dict["uuid"]
            if pub_uuid:
                host_sql.pub_uuid = pub_uuid
            else:
                host_sql.pub_uuid = generate_uuid(public=True)
        else:
            # Propagate changes in public UUID
            if pub_uuid:
                host_sql.pub_uuid = pub_uuid
        # Fix lsb vs release error in F11.
        if host_dict['os'] == 'Fedora 11 Leonidas':
            host_sql.os = 'Fedora release 11 (Leonidas)'
        else:
            host_sql.os = host_dict['os']
        host_sql.default_runlevel = 0 if host_dict['default_runlevel'] == 'Unknown' else host_dict['default_runlevel']
        host_sql.language = host_dict['language']
        host_sql.platform = host_dict['platform']
        host_sql.bogomips = 0 if not host_dict['bogomips'] else host_dict['bogomips']
        host_sql.cpu_vendor = host_dict['cpu_vendor']
        host_sql.cpu_model = host_dict['cpu_model']
        host_sql.cpu_speed = host_dict['cpu_speed']
        host_sql.num_cpus = host_dict['num_cpus']
        host_sql.system_memory = host_dict['system_memory']
        host_sql.system_swap = host_dict['system_swap']
        host_sql.vendor = _fix_vendor(host_dict['vendor'])
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

        orig_devices = [device.device_id for device
                                        in host_sql.devices]

        for device in host_dict['devices']:
            description = device['description'].encode('UTF8')
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
                    session.add(class_sql)
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

        host_sql = self.extend_host_sql_hook(host_sql, host_dict)

        return dict(pub_uuid=host_sql.pub_uuid)
