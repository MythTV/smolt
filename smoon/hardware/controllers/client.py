# -*- coding: utf-8 -*-
import simplejson

from turbogears import expose
from turbogears import exception_handler
from turbogears import util
from sqlalchemy.exceptions import InvalidRequestError, OperationalError
from datetime import datetime

from urllib import quote

from hardware.wiki import *
from hardware.ratingwidget import *
from hardware.controllers.error import Error
from hardware.model import *
from hardware.hwdata import DeviceMap
from hardware.uuid import generate_uuid
from hardware.submission import handle_submission

import gc

#added to detect myth support
from turbogears import config
myth_support = config.config.configMap["global"].get("smoon.myth_support", False)


def request_format():
    format = cherrypy.request.params.get('tg_format', '').lower()
    if not format:
        format = cherrypy.request.headers.get('Accept', 'default').lower()
    return format

def _fix_vendor(vendor):
    rc = vendor
    if vendor.startswith('Dell'):
        rc = 'Dell, Inc.'
    return rc


class Client(object):
    error = Error()
    def __init__(self, smolt_protocol, token):
        self.smolt_protocol = smolt_protocol
        self.token = token

    @expose(template="hardware.templates.show", allow_json=True)
    @exception_handler(error.error_web,rules="isinstance(tg_exceptions,ValueError)")
    def show(self, uuid='', UUID=None, admin=None):

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
    @expose(template="hardware.templates.showall", allow_json=True)
    @exception_handler(error.error_web,rules="isinstance(tg_exceptions,ValueError)")
    def show_all(self, uuid='', admin=None):
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

    @expose(template="hardware.templates.delete")
    @exception_handler(error.error_client,rules="isinstance(tg_exceptions,ValueError)")
    def delete(self, uuid=''):
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

    @expose("json")
    @exception_handler(error.error_client,rules="isinstance(tg_exceptions,ValueError)")
    def host_rating(self, vendor, system):
        q = session.query(Host).filter_by(vendor=vendor, system=system).add_column(func.count(Host.rating).label('count')).group_by(Host.rating)
        ratings = {}
        for rate in q:
            ratings[rate[0].rating] = rate[1]
        return dict(ratings=ratings)

    @expose("json")
    @exception_handler(error.error_client,rules="isinstance(tg_exceptions,ValueError)")
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

    @expose(template="hardware.templates.pub_uuid")
    @exception_handler(error.error_client, rules="isinstance(tg_exceptions,ValueError)")
    def add_json(self, uuid, host, token, smolt_protocol):
        self._run_add_json_checks(uuid, host, token, smolt_protocol)
        res = handle_submission(session, uuid, host)
        log_entry = BatchJob(host, uuid, added=True)
        session.add(log_entry)
        session.flush()

        return res

    @expose()
    def rate_object(self, *args, **kwargs):
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

    @expose()
    def batch_add_json(self, uuid, host, token, smolt_protocol):
        self._run_add_json_checks(uuid, host, token, smolt_protocol)
        job = BatchJob(host, uuid, added=False)
        session.add(job)
        session.flush()
        return dict()

    @expose()
    def pub_uuid(self, uuid):
        pub_uuid=select([Host.pub_uuid], Host.uuid==uuid).execute().fetchone()[0]
        return dict(pub_uuid=pub_uuid)

    def new_pub_uuid(self, uuid):
        #TODO
        pass


