# -*- coding: utf-8 -*-
# smolt - Fedora hardware profiler
#
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



import copy
import traceback

import sqlalchemy
from sqlalchemy.orm import eagerload
from turbogears.database import session

from hardware.model.model_mythtv import *
from hardware.model.model import *
from hardware.controllers.client_impl import ClientImplementation


class MythTvClientImplementation(ClientImplementation):
    def data_for_next_hop(self, host_dict):
        #host_dict is a string, so this won't work
        #TODO
        deep_copy = copy.copy(host_dict)
        try:
            del deep_copy['distro_specific']['mythtv']
            if not deep_copy['distro_specific']:
                del deep_copy['distro_specific']
        except KeyError:
            pass
        return deep_copy

    def extend_host_sql_hook(self, host_sql, host_dict):
        _handle_mythtv_data(session, host_dict, host_sql.id)
        return host_sql


def _handle_simple_stuff(session, data, machine_id , myth_uuid):

    try:
        myth_branch = data['features']['branch']
    except:
        myth_branch = "unknown"


    try:
        myth_language = data['features']['language']
    except:
        myth_language = "unknown"

    try:
        myth_libapi = data['features']['libapi']
    except:
        myth_libapi = "unknown"

    try:
        myth_protocol = data['features']['protocol']
    except:
        myth_protocol = "unknown"

    try:
        myth_sourcecount = data['features']['sourcecount']
    except:
        myth_sourcecount = "0"

    try:
        myth_theme = data['features']['theme']
    except:
        myth_theme = "unknown"

    if myth_theme == None:
        myth_theme = "unknown"

    try:
        myth_timezone = data['features']['timezone']
    except:
        myth_timezone = "unknown"

    try:
        myth_country = data['features']['country']
    except:
        myth_country = "unknown"


    try:
        myth_tzoffset = data['features']['tzoffset']
    except:
        myth_tzoffset = -999999

    try:
        myth_version = data['features']['version']
    except:
        myth_version = "unknown"

    myth_version_bucket = myth_version.split("-")[0]


    try:
        qt_version = data['features']['qtversion']
    except:
        qt_version = "unknown"

    try:
        channel_count = data['features']['channel_count']
    except:
        channel_count = "0"

    try:
        remote = data['features']['remote']
    except:
        remote = "unknown"

    try:
        myth_type = data['features']['mythtype']
    except:
        myth_type = "-1"

    try:
        vtpertuner = data['features']['vtpertuner']
    except:
        vtpertuner = None

    #Remove old entry
    session.query(mythtvHost).filter_by(machine_id = machine_id).delete()
    session.add(mythtvHost(data,myth_branch,
                          myth_uuid,
                          myth_language,
                          myth_libapi,
                          myth_protocol,
                          myth_sourcecount,
                          myth_theme,
                          myth_timezone,
                          myth_country,
                          myth_tzoffset,
                          myth_version,
                          myth_version_bucket,
                          qt_version,
                          channel_count,
                          remote,
                          myth_type,
                          vtpertuner,
                          machine_id))

    session.flush()


def _handle_audio(session, data, machine_id):
    passthru = 'None'
    steropcm = -1
    upmixtype = 'None'
    volcontrol = -1
    defaultupmix = -1
    maxchannels = -1
    passthruoverride = -1
    mixercontrol = "None"
    sr_override = -1
    passthrudevice = "None"
    device = "None"
    mixerdevice = "None"
    audio_sys = "None"
    audio_sys_version = "unknown"
    jack = -1
    pulse = -1

    try:
        myth_audio = data['features']['audio']
    except:
        myth_audio = {}

    try:
        pass_thru = myth_audio['passthru']
    except:
        pass

    try:
        steropcm = int(myth_audio['steropcm'])
    except:
        pass

    try:
        upmixtype = myth_audio['upmixtype']
    except:
        pass

    try:
        volcontrol = int(myth_audio['volcontrol'])
    except:
        pass

    try:
        defaultupmix = int(myth_audio['defaultupmix'])
    except:
        pass

    try:
        maxchannels = myth_audio['maxchannels']
    except:
        pass

    try:
        passthruoverride = int(myth_audio['passthruoverride'])
    except:
        pass

    try:
        maxercontrol = myth_audio['mixercontrol']
    except:
        pass

    try:
        sr_override = int(myth_audio['sr_override'])
    except:
        pass

    try:
        passthrudevice = myth_audio['passthrudevice']
    except:
        pass

    try:
        device = myth_audio['device']

    except:
        pass

    try:
        mixerdevice = myth_audio['mixerdevice']
    except:
        pass

    try:
        audio_sys = myth_audio['audio_sys']
    except:
        pass

    try:
        audio_sys_version = myth_audio['audio_sys_version']
    except:
        pass

    try:
        jack = myth_audio['jack']
    except:
        pass

    try:
        pulse = myth_audio['pulse']
    except:
        pass


    #Remove old entry
    session.query(mythtvAudio).filter_by(machine_id = machine_id).delete()



    session.add(mythtvAudio(machine_id,
                            passthru,steropcm,
                            upmixtype, volcontrol,
                            defaultupmix, maxchannels,
                            passthruoverride, mixercontrol,
                            sr_override, passthrudevice,
                            device, mixerdevice, audio_sys,
                            audio_sys_version,jack, pulse)
                            )

    session.flush()

def _handle_db(session, data,  myth_uuid):
    version = "-1"
    usedengine = "unknown"
    engines = ['unknown']
    schemas = ['unknown']
    try:
        myth_db = data['features']['database']
    except:
        myth_db = {}

    try:
        version = myth_db['version']
    except:
        pass

    try:
        usedengine = myth_db['usedengine']
    except:
        pass

    try:
        engines = myth_db['engines']
    except:
        pass

    try:
        schemas = myth_db['schema']
    except:
        pass
    #Remove old entry
    #session.query(mythtvDatabase).filter_by(machine_id = machine_id).delete()
    session.query(mythtvDatabase).filter_by(myth_uuid = myth_uuid).delete()
    #Add new entry
    session.add(mythtvDatabase(myth_uuid,
                               version, usedengine,
                               engines, schemas)
                               )

    session.flush()

def _handle_grabbers(session, data, myth_uuid):


    session.query(mythtvGrabbers).filter_by(myth_uuid = myth_uuid).delete()
    try:
        myth_grabber = data['features']['grabbers']
    except:
        myth_grabber=['unknown']

    for i in myth_grabber:
        if i:
            session.add(mythtvGrabbers(myth_uuid,i))
    session.flush()

def _handle_historical(session, data,myth_uuid):
    showcount = 0
    rectime = 0
    db_age = 0
    reccount = 0
    try:
        myth_hist = data['features']['historical']
    except:
        myth_hist = {}

    #session.query(mythtvHistorical).filter_by(machine_id = machine_id).delete()
    session.query(mythtvHistorical).filter_by(myth_uuid = myth_uuid).delete()

    try:
        showcount = myth_hist['showcount']
    except:
        pass

    try:
        rectime = myth_hist['rectime']
    except:
        pass
    try:
        db_age = myth_hist['db_age']
    except:
        pass
    try:
        reccount = myth_hist['reccount']
    except:
        pass

    session.add(mythtvHistorical(myth_uuid,
                                 showcount,rectime,db_age,reccount)
                                 )
    session.flush()


def _handle_pbp(session, data, machine_id):

    name = "unknown"
    profiles = ['unknown']

    try:
        myth_pb = data['features']['playbackprofile']
    except:
        myth_pb = {}

    try:
        name = myth_pb['name']
    except:
        pass


    try:
        profiles = myth_pb['profiles']
    except:
        pass

    #Remove old entry
    session.query(mythtvPbp).filter_by(machine_id = machine_id).delete()
    #Add new entry
    session.add(mythtvPbp(machine_id,name,profiles))
    session.flush()

def _handle_recordings(session, data, myth_uuid):
    sched_count = -1
    sched_time = -1
    sched_size = -1
    live_count = -1
    live_time = -1
    live_size = -1
    exp_count = -1
    exp_time = -1
    exp_size = -1
    upcoming_count = -1
    upcoming_time = -1

    try:
        myth_rec = data['features']['recordings']
    except:
        myth_rec = {}

    try:
        sched = myth_rec['scheduled']
    except:
        pass
    try:
        live = myth_rec['livetv']
    except:
        pass
    try:
         expire = myth_rec['expireable']
    except:
        pass
    try:
        upcoming = myth_rec['upcoming']
    except:
        pass
    #pull out each item for scheduled,live,expire,upcoming.
    try:
        sched_count = sched['count']
    except:
        pass

    try:
        sched_time = sched['time']
    except:
        pass

    try:
        sched_size = sched['size']
    except:
        pass


    try:
        live_count = live['count']
    except:
        pass

    try:
        live_time = live['time']
    except:
        pass

    try:
        live_size = live['size']
    except:
        pass

    try:
        exp_count = expire['count']
    except:
        pass

    try:
        exp_time = expire['time']
    except:
        pass

    try:
        exp_size = expire['size']
    except:
        pass

    try:
        upcoming_count = upcoming['count']
    except:
        pass

    try:
        upcoming_time = upcoming['time']
    except:
        pass


    #session.query(mythtvRecordings).filter_by(machine_id = machine_id).delete()
    session.query(mythtvRecordings).filter_by(myth_uuid = myth_uuid).delete()
    session.add(mythtvRecordings(myth_uuid,
                                sched_count, sched_time,
                                sched_size, live_count,
                                live_time, live_size,
                                exp_count, exp_time,
                                exp_size, upcoming_count,
                                upcoming_time)
                                )

    session.flush()


def _handle_scheduler(session, data, myth_uuid):

    count = 0
    place_stddev = 0
    match_stddev = 0
    match_avg = 0
    place_avg = 0


    try:
        myth_sch = data['features']['scheduler']
    except:
        myth_sch = {}

    try:
        count = myth_sch['count']
    except:
        pass

    try:
        place_stddev = myth_sch['place_stddev']
    except:
        pass

    try:
        match_stddev = myth_sch['match_stddev']
    except:
        pass

    try:
        match_avg = myth_sch['match_avg']
    except:
        pass

    try:
        place_avg = myth_sch['place_avg']
    except:
        pass

    #Remove old entry
    session.query(mythtvScheduler).filter_by(myth_uuid = myth_uuid).delete()
    #Add new entry
    session.add(mythtvScheduler(myth_uuid,
                                count, place_stddev,
                                match_stddev, match_avg,
                                place_avg)
                                )
    session.flush()

def _handle_storage(session, data, myth_uuid ):
    rectotal = -1
    recfree = -1
    videototal = -1
    videofree = -1

    try:
        myth_storage = data['features']['storage']
    except:
        myth_storage = {}

    try:
        rectotal = myth_storage['rectotal']
    except:
        pass

    try:
        recfree = myth_storage['recfree']
    except:
        pass

    try:
        videototal = myth_storage['videototal']
    except:
        pass

    try:
        videofree = myth_storage['videofree']
    except:
        pass

    #Remove old entry
    session.query(mythtvStorage).filter_by(myth_uuid = myth_uuid).delete()
    #Add new entry
    session.add(mythtvStorage(myth_uuid,
                              rectotal, recfree,
                              videototal, videofree)
                              )
    session.flush()



def _handle_tuners(session, data, myth_uuid):

    session.query(mythtvtuners).filter_by(myth_uuid = myth_uuid).delete()
    try:
        myth_tunner = data['features']['tuners']
    except:
        myth_tunner={'unknown':0}


    for key,value in myth_tunner.items():
        session.add(mythtvtuners(myth_uuid,key,value))
    session.flush()

def _handle_logs(session, data, myth_uuid):
    crit = -1
    info = -1
    notice = -1
    warning = -1
    err = -1

    try:
        myth_log = data['features']['logurgency']
    except:
        myth_log = {}

    try:
        crit = myth_log['CRIT']
    except:
        pass
    try:
        info = myth_log['INFO']
    except:
        pass
    try:
        notice = myth_log['NOTICE']
    except:
        pass
    try:
        warning = myth_log['WARNING']
    except:
        pass
    try:
        err = myth_log['ERR']
    except:
        pass
  #Remove old entry
    session.query(mythtvLogUrgency).filter_by(myth_uuid = myth_uuid).delete()
    #Add new entry
    session.add(mythtvLogUrgency(myth_uuid,
                                crit,
                                info,
                                notice,
                                warning,
                                err))
    session.flush()





def _handle_mythtv_data(session, host_dict, machine_id):
    try:
        data = host_dict['distro_specific']['mythtv']

    except KeyError:
        logging.debug('No Mythtv-specific data')
        print "no mythtv-specific data"
        data = {}

    try:
        myth_uuid = data['features']['uuid']
    except:
        myth_uuid = "unknown"

    try:
        _handle_simple_stuff(session, data, machine_id, myth_uuid)
        _handle_audio(session, data, machine_id)
        _handle_db(session, data, myth_uuid)
        _handle_grabbers(session, data, myth_uuid)
        _handle_historical(session, data,  myth_uuid)
        _handle_pbp(session,data,machine_id)
        _handle_recordings(session,data,myth_uuid)
        _handle_scheduler(session,data, myth_uuid)
        _handle_storage(session,data, myth_uuid)
        _handle_tuners(session,data, myth_uuid)
        _handle_logs(session,data, myth_uuid)

    except Exception, e:
        traceback.print_tb(sys.exc_info()[2])
        raise e