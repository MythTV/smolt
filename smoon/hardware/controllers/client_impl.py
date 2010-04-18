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

from sqlalchemy.exceptions import InvalidRequestError
from turbogears.database import session

from hardware.submission import handle_submission
from hardware.hwdata import DeviceMap
from hardware.model import BatchJob, Host
from hardware.wiki import getDeviceWikiLink, getHostWikiLink, getOSWikiLink
from hardware.ratingwidget import SingleRatingWidget


class ClientImplementation(object):
    def __init__(self, smolt_protocol, token):
        self.smolt_protocol = smolt_protocol
        self.token = token

    def data_for_next_hop(self, host_dict):
        return copy.copy(host_dict)  # TODO

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
        q = session.query(Host).filter_by(vendor=vendor, system=system).add_column(func.count(Host.rating).label('count')).group_by(Host.rating)
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

    def add_json(self, uuid, host, token, smolt_protocol):
        self._run_add_json_checks(uuid, host, token, smolt_protocol)
        res = handle_submission(session, uuid, host)
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
