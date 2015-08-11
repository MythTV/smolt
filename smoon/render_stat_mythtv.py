from __future__ import division
from turbogears.database import session
from turbogears import view, database, errorhandling, config
from hardware.turboflot import TurboFlot
from hardware.featureset import init, config_filename, at_final_server
from hardware.featureset import this_is, MYTH_TV
from hardware.model import *
#from numpy import *
#using numpy
#chan_list = array(list((session.query(mythtvHost)
#.filter((mythtvHost.last_modified > now))
#.values(mythtvHost.channel_count))))

    #print chan_list.max()
    #print chan_list.min()
    #print chan_list.mean()
    #print chan_list.std()



def humanize_bytes(bytes, precision=1):
    #http://code.activestate.com/recipes/577081-humanized-representation-of-a-number-of-bytes/
    abbrevs = (
    (1<<50L, 'PB'),
    (1<<40L, 'TB'),
    (1<<30L, 'GB'),
    (1<<20L, 'MB'),
    (1<<10L, 'kB'),
    (1, 'bytes')
    )
    if bytes == 1:
        return '1 byte'
    for factor, suffix in abbrevs:
        if bytes >= factor:
            break
    return '%.*f %s' % (precision, bytes / factor, suffix)



#taken from render-stat
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




def render_mythtv(stats):
    right_now = date.today() - timedelta(days=90)
    right_now = '%s-%s-%s' % (right_now.year, right_now.month, right_now.day)
    now = date.today() - timedelta(days=90)

    WITHHELD_MAGIC_STRING = 'WITHHELD'
    withheld_label = "withheld"

    from hardware.model.myth_views import myth_import_string
    exec(myth_import_string)

    print '====================== Myth_language stats ======================'
    from hardware.model.model_mythtv import mythtvHistorical,mythtvHost,mythtvGrabbers, mythtvAudio,mythtvHistorical, mythtvScheduler,mythtvStorage,mythtvDatabase,mythtvRecordings,mythtvHost,mythtvtuners,mythtvLogUrgency
    from hardware.model.model_mythtv import mythtv_host, mythtv_tuners
    stats["total_mh"] =  session.query(mythtvHost).filter(mythtvHost.last_modified > (date.today() - timedelta(days=90))).count()

    stats["total_mc"] =  session.query(mythtvHost.myth_uuid).filter(mythtvHost.last_modified > (date.today() - timedelta(days=90))).distinct().count()

    stats["total_grabber"] =  session.query(mythtvGrabbers).filter(mythtvGrabbers.last_modified > (date.today() - timedelta(days=90))).count()




    stats['myth_language'] = handle_withheld_elem(
            session.query(MythLanguage).all(),
            'language', WITHHELD_MAGIC_STRING)

    stats['myth_theme'] = handle_withheld_elem(
            session.query(MythTheme).all(),
            'theme', WITHHELD_MAGIC_STRING)

    stats['myth_timezone'] = handle_withheld_elem(
            session.query(MythTimezone).all(),
            'timezone', WITHHELD_MAGIC_STRING)


    stats['myth_country'] = handle_withheld_elem(
            session.query(MythCountry).all(),
            'country', WITHHELD_MAGIC_STRING)

    stats['myth_version'] = handle_withheld_elem(
            session.query(MythVersion).all(),
            'myth_version_bucket', WITHHELD_MAGIC_STRING)

    stats['myth_sourcecount'] = handle_withheld_elem(
            session.query(MythSourceCount).all(),
            'sourcecount', WITHHELD_MAGIC_STRING)

    stats['myth_dbversion'] = handle_withheld_elem(
            session.query(MythDbVersion).all(),
            'version', WITHHELD_MAGIC_STRING)
    #group mysql version to major,minor version.  Skip point release
    db_version={}
    for a in stats["myth_dbversion"]:
        temp_tuple=()
        split_string=a.version.split(".",2)
        bucket_version = ".".join(split_string[0:2])
        if bucket_version in db_version:
            db_version[bucket_version] += a.cnt
        else:
            db_version[bucket_version] = a.cnt

    stats['myth_dbversion'] = db_version

    stats['myth_qtversion'] = handle_withheld_elem(
            session.query(MythQTVersion).all(),
            'qt_version', WITHHELD_MAGIC_STRING)

    stats['myth_branch'] = handle_withheld_elem(
            session.query(MythBranch).all(),
            'branch', WITHHELD_MAGIC_STRING)

    stats['myth_grabber'] = handle_withheld_elem(
            session.query(MythGrabber).all(),
            'grabber', WITHHELD_MAGIC_STRING)

    sec_year = 31556926

    stats['myth_dbage'] = []
    #stat = session.query(func.min(mythtvHistorical.db_age))[0]
    stat = list(session.query(mythtvHistorical).filter((mythtvHistorical.last_modified > now)).values(func.min(mythtvHistorical.db_age)))[0]
    stats['myth_dbage'].append(("minimum",stat))

    #stat = session.query(func.max(mythtvHistorical.db_age))[0]
    stat = list(session.query(mythtvHistorical).filter((mythtvHistorical.last_modified > now)).values(func.max(mythtvHistorical.db_age)))[0]
    try:
        maxstat = int(stat[0]/sec_year)
    except:
        maxstat = 0
    stats['myth_dbage'].append(("maximum",stat))

    #stat = session.query(func.avg(mythtvHistorical.db_age))[0]
    stat = list(session.query(mythtvHistorical).filter((mythtvHistorical.last_modified > now)).values(func.avg(mythtvHistorical.db_age)))[0]
    stats['myth_dbage'].append(("average",stat))


    #dbage break down
    stats['myth_dbage_g'] = []
    #dbcount = session.query(mythtvHistorical).filter(and_(mythtvHistorical.db_age != -1, mythtvHistorical.db_age <= (sec_year)), ).count()
    dbcount = session.query(mythtvHistorical).filter(and_(
              mythtvHistorical.db_age != -1,
              mythtvHistorical.db_age <= (sec_year),
              mythtvHistorical.last_modified > now )).count()


    stats['myth_dbage_g'].append(("Less then one year",dbcount))

    for i in range(1, maxstat+1):
        dbcount = session.query(mythtvHistorical).filter(and_(
            mythtvHistorical.db_age != -1,
            mythtvHistorical.db_age >= (i*sec_year),
            mythtvHistorical.db_age < ((i+1)*sec_year),
            mythtvHistorical.last_modified > now)).count()

        if int(dbcount) > 0:
            text = " Between %s and %s years" %(i,i+1)
            stats['myth_dbage_g'].append((text,dbcount))


#------------------Channel count -------------

    stats['myth_chan_count'] = []
    stat = list(session.query(mythtvHost)
        .filter((mythtvHost.last_modified > now))
        .values(func.min(mythtvHost.channel_count)))[0]
    stats['myth_chan_count'].append(("Channel Count minimum",stat))

    stat = list(session.query(mythtvHost)
        .filter((mythtvHost.last_modified > now))
        .values(func.max(mythtvHost.channel_count)))[0]
    stats['myth_chan_count'].append(("Channel Count maximum",stat))

    stat = list(session.query(mythtvHost)
        .filter((mythtvHost.last_modified > now))
        .values(func.avg(mythtvHost.channel_count)))[0]
    stats['myth_chan_count'].append(("Channel Count average",stat))

    stat = list(session.query(mythtvHost)
        .filter((mythtvHost.last_modified > now))
        .values(func.stddev(mythtvHost.channel_count)))[0]
    stats['myth_chan_count'].append(("Channel Count standard deviation",stat))
    #------------------------------------------------------------------
    stats['myth_sched_count'] = []
    #stat = session.query(func.min(mythtvScheduler.count))[0]
    stat = list(session.query(mythtvScheduler).filter((mythtvScheduler.last_modified > now)).values(func.min(mythtvScheduler.count)))[0]
    stats['myth_sched_count'].append(("Scheduled Episodes minimum",stat))
    #stat = session.query(func.max(mythtvScheduler.count))[0]
    stat = list(session.query(mythtvScheduler).filter((mythtvScheduler.last_modified > now)).values(func.max(mythtvScheduler.count)))[0]
    stats['myth_sched_count'].append(("Scheduled Episodes maximum",stat))
    #stat = session.query(func.avg(mythtvScheduler.count))[0]
    stat = list(session.query(mythtvScheduler).filter((mythtvScheduler.last_modified > now)).values(func.avg(mythtvScheduler.count)))[0]
    stats['myth_sched_count'].append(("Scheduled Episodes average",stat))
    stat = list(session.query(mythtvScheduler).filter((mythtvScheduler.last_modified > now)).values(func.stddev(mythtvScheduler.count)))[0]
    stats['myth_sched_count'].append(("Scheduled Episodes standard deviation",stat))
    #------------------------------------------------------------------
    stats['myth_showcount'] = []
    stat = list(session.query(mythtvHistorical)
        .filter((mythtvHistorical.last_modified > now))
        .filter((mythtvHistorical.showcount  > -1 ))
        .values(func.min(mythtvHistorical.showcount)))[0]
    stats['myth_showcount'].append(("Show/Series Count minimum",stat))

    stat = list(session.query(mythtvHistorical)
        .filter((mythtvHistorical.last_modified > now))
        .filter((mythtvHistorical.showcount  > -1 ))
        .values(func.max(mythtvHistorical.showcount)))[0]
    stats['myth_showcount'].append(("Show/Series Count maximum",stat))

    stat = list(session.query(mythtvHistorical)
        .filter((mythtvHistorical.last_modified > now))
        .filter((mythtvHistorical.showcount  > -1 ))
        .values(func.avg(mythtvHistorical.showcount)))[0]
    stats['myth_showcount'].append(("Show/Series Count average",stat))
    stat = list(session.query(mythtvHistorical)
        .filter((mythtvHistorical.last_modified > now))
        .filter((mythtvHistorical.showcount  > -1 ))
        .values(func.stddev(mythtvHistorical.showcount)))[0]
    stats['myth_showcount'].append(("Show/Series Count standard deviation",stat))
    #------------------------------------------------------------------
    stats['myth_reccount'] = []
    stat = list(session.query(mythtvHistorical)
        .filter((mythtvHistorical.last_modified > now))
        .filter((mythtvHistorical.reccount > -1 ))
        .values(func.min(mythtvHistorical.reccount)))[0]
    stats['myth_reccount'].append(("Overall Recordings minimum",stat))
    stat = list(session.query(mythtvHistorical)
        .filter((mythtvHistorical.last_modified > now))
        .filter((mythtvHistorical.reccount > -1 ))
        .values(func.max(mythtvHistorical.reccount)))[0]
    stats['myth_reccount'].append(("Overall Recordings maximum",stat))
    stat = list(session.query(mythtvHistorical)
        .filter((mythtvHistorical.last_modified > now))
        .filter((mythtvHistorical.reccount > -1 ))
        .values(func.avg(mythtvHistorical.reccount)))[0]
    stats['myth_reccount'].append(("Overall Recordings average",stat))
    stat = list(session.query(mythtvHistorical)
        .filter((mythtvHistorical.last_modified > now))
        .filter((mythtvHistorical.reccount > -1 ))
        .values(func.stddev(mythtvHistorical.reccount)))[0]
    stats['myth_reccount'].append(("Overall Recordings standard deviation",stat))
    #------------------------------------------------------------------
    stats['myth_recordings_rc'] = []
    stat = list(session.query(mythtvRecordings)
        .filter((mythtvRecordings.last_modified > now))
        .filter((mythtvRecordings.sched_count > -1 ))
        .values(func.min(mythtvRecordings.sched_count)))[0]
    stats['myth_recordings_rc'].append(("Recorded shows minimum",stat))
    stat = list(session.query(mythtvRecordings)
        .filter((mythtvRecordings.last_modified > now))
        .filter((mythtvRecordings.sched_count > -1 ))
        .values(func.max(mythtvRecordings.sched_count)))[0]
    stats['myth_recordings_rc'].append(("Recorded shows maximum",stat))
    stat = list(session.query(mythtvRecordings)
        .filter((mythtvRecordings.last_modified > now))
        .filter((mythtvRecordings.sched_count > -1 ))
        .values(func.avg(mythtvRecordings.sched_count)))[0]
    stats['myth_recordings_rc'].append(("Recorded shows average",stat))

    stat = list(session.query(mythtvRecordings)
        .filter((mythtvRecordings.last_modified > now))
        .filter((mythtvRecordings.sched_count > -1 ))
        .values(func.stddev(mythtvRecordings.sched_count)))[0]
    stats['myth_recordings_rc'].append(("Recorded shows standard deviation",stat))
    #------------------------------------------------------------------
    stats['myth_recordings_live'] = []
    stat = list(session.query(mythtvRecordings)
        .filter((mythtvRecordings.last_modified > now))
        .filter((mythtvRecordings.live_count > -1))
        .values(func.min(mythtvRecordings.live_count)))[0]
    stats['myth_recordings_live'].append(("Live TV  minimum",stat))

    stat = list(session.query(mythtvRecordings)
        .filter((mythtvRecordings.last_modified > now))
        .filter((mythtvRecordings.live_count > -1))
        .values(func.max(mythtvRecordings.live_count)))[0]
    stats['myth_recordings_live'].append(("Live TV maximum",stat))
    stat = list(session.query(mythtvRecordings)
        .filter((mythtvRecordings.last_modified > now))
        .filter((mythtvRecordings.live_count > -1))
        .values(func.avg(mythtvRecordings.live_count)))[0]
    stats['myth_recordings_live'].append(("Live TV average",stat))
    stat = list(session.query(mythtvRecordings)
        .filter((mythtvRecordings.last_modified > now))
        .filter((mythtvRecordings.live_count > -1))
        .values(func.stddev(mythtvRecordings.live_count)))[0]
    stats['myth_recordings_live'].append(("Live TV Standard Deviation",stat))
    #------------------------------------------------------------------
    stats['myth_recordings_upcoming'] = []
    stat = list(session.query(mythtvRecordings)
        .filter((mythtvRecordings.last_modified > now))
        .filter((mythtvRecordings.upcoming_count > -1))
        .values(func.min(mythtvRecordings.upcoming_count)))[0]
    stats['myth_recordings_upcoming'].append(("Upcoming shows minimum",stat))

    stat = list(session.query(mythtvRecordings)
        .filter((mythtvRecordings.last_modified > now))
        .filter((mythtvRecordings.upcoming_count > -1))
        .values(func.max(mythtvRecordings.upcoming_count)))[0]
    stats['myth_recordings_upcoming'].append(("Upcoming shows maximum",stat))

    stat = list(session.query(mythtvRecordings)
        .filter((mythtvRecordings.last_modified > now))
        .filter((mythtvRecordings.upcoming_count > -1))
        .values(func.avg(mythtvRecordings.upcoming_count)))[0]
    stats['myth_recordings_upcoming'].append(("Upcoming shows average",stat))

    stat = list(session.query(mythtvRecordings)
        .filter((mythtvRecordings.last_modified > now))
        .filter((mythtvRecordings.upcoming_count > -1))
        .values(func.stddev(mythtvRecordings.upcoming_count)))[0]
    stats['myth_recordings_upcoming'].append(("Upcoming shows standard deviation",stat))
    #------------------------------------------------------------------
    stats['myth_recordings_expire'] = []
    stat = list(session.query(mythtvRecordings)
        .filter((mythtvRecordings.last_modified > now))
        .filter((mythtvRecordings.exp_count > -1))
        .values(func.min(mythtvRecordings.exp_count)))[0]
    stats['myth_recordings_expire'].append(("Expire shows minimum",stat))

    stat = list(session.query(mythtvRecordings)
        .filter((mythtvRecordings.last_modified > now))
        .filter((mythtvRecordings.exp_count > -1))
        .values(func.max(mythtvRecordings.exp_count)))[0]
    stats['myth_recordings_expire'].append(("Expire shows maximum",stat))

    stat = list(session.query(mythtvRecordings)
        .filter((mythtvRecordings.last_modified > now))
        .filter((mythtvRecordings.exp_count > -1))
        .values(func.avg(mythtvRecordings.exp_count)))[0]
    stats['myth_recordings_expire'].append(("Expire shows average",stat))

    stat = list(session.query(mythtvRecordings)
        .filter((mythtvRecordings.last_modified > now))
        .filter((mythtvRecordings.exp_count > -1))
        .values(func.stddev(mythtvRecordings.exp_count)))[0]
    stats['myth_recordings_expire'].append(("Expire shows standard deviation",stat))
    #------------------------------------------------------------------
    stats['myth_storage_rt'] = []
    stat = list(session.query(mythtvStorage)
        .filter((mythtvStorage.last_modified > now))
        .filter((mythtvStorage.rectotal > 0 ))
        .values(func.min(mythtvStorage.rectotal)))[0][0]
    stats['myth_storage_rt'].append(("Recorded storage minimum",humanize_bytes(stat)))
    stat = list(session.query(mythtvStorage)
        .filter((mythtvStorage.last_modified > now))
        .filter((mythtvStorage.rectotal > 0 ))
        .values(func.max(mythtvStorage.rectotal)))[0][0]
    stats['myth_storage_rt'].append(("Recorded storage maximum",humanize_bytes(stat)))
    stat = list(session.query(mythtvStorage)
        .filter((mythtvStorage.last_modified > now))
        .filter((mythtvStorage.rectotal > 0 ))
        .values(func.avg(mythtvStorage.rectotal)))[0][0]
    stats['myth_storage_rt'].append(("Recorded storage average",humanize_bytes(stat)))

    stat = list(session.query(mythtvStorage)
        .filter((mythtvStorage.last_modified > now))
        .filter((mythtvStorage.rectotal > 0 ))
        .values(func.stddev(mythtvStorage.rectotal)))[0][0]
    stats['myth_storage_rt'].append(("Recorded storage standard deviation",humanize_bytes(stat)))
    #------------------------------------------------------------------
    stats['myth_storage_rf'] = []
    #stat = session.query(func.min(mythtvStorage.recfree))[0]
    stat = list(session.query(mythtvStorage)
        .filter((mythtvStorage.last_modified > now))
        .filter((mythtvStorage.recfree > 0 ))
        .values(func.min(mythtvStorage.recfree)))[0][0]

    stats['myth_storage_rf'].append(("Recorded free minimum",humanize_bytes(stat)))
    stat = list(session.query(mythtvStorage)
        .filter((mythtvStorage.last_modified > now))
        .filter((mythtvStorage.recfree > 0 ))
        .values(func.max(mythtvStorage.recfree)))[0][0]
    stats['myth_storage_rf'].append(("Recorded free maximum",humanize_bytes(stat)))

    stat = list(session.query(mythtvStorage)
        .filter((mythtvStorage.last_modified > now))
        .filter((mythtvStorage.recfree > 0 ))
        .values(func.avg(mythtvStorage.recfree)))[0][0]
    stats['myth_storage_rf'].append(("Recorded free average",humanize_bytes(stat)))

    stat = list(session.query(mythtvStorage)
        .filter((mythtvStorage.last_modified > now))
        .filter((mythtvStorage.recfree > 0 ))
        .values(func.stddev(mythtvStorage.recfree)))[0][0]
    stats['myth_storage_rf'].append(("Recorded free standard deviation",humanize_bytes(stat)))
    #------------------------------------------------------------------
    stats['myth_storage_vt'] = []
    stat = list(session.query(mythtvStorage)
        .filter((mythtvStorage.last_modified > now))
        .filter((mythtvStorage.videototal > 0))
        .values(func.min(mythtvStorage.videototal)))[0][0]
    stats['myth_storage_vt'].append(("Video storage minimum",humanize_bytes(stat)))
    stat = list(session.query(mythtvStorage)
        .filter((mythtvStorage.last_modified > now))
        .filter((mythtvStorage.videototal > 0))
        .values(func.max(mythtvStorage.videototal)))[0][0]
    stats['myth_storage_vt'].append(("Video storage maximum",humanize_bytes(stat)))
    stat = list(session.query(mythtvStorage)
        .filter((mythtvStorage.last_modified > now))
        .filter((mythtvStorage.videototal > 0))
        .values(func.avg(mythtvStorage.videototal)))[0][0]
    stats['myth_storage_vt'].append(("Video storage average",humanize_bytes(stat)))
    stat = list(session.query(mythtvStorage)
        .filter((mythtvStorage.last_modified > now))
        .filter((mythtvStorage.videototal > 0))
        .values(func.stddev(mythtvStorage.videototal)))[0][0]
    stats['myth_storage_vt'].append(("Video storage standard deviation",humanize_bytes(stat)))
    #------------------------------------------------------------------
    stats['myth_storage_vf'] = []
    stat = list(session.query(mythtvStorage)
        .filter((mythtvStorage.last_modified > now))
        .filter((mythtvStorage.videofree > 0))
        .values(func.min(mythtvStorage.videofree)))[0][0]
    stats['myth_storage_vf'].append(("Video free minimum",humanize_bytes(stat)))
    stat = list(session.query(mythtvStorage)
        .filter((mythtvStorage.last_modified > now))
        .filter((mythtvStorage.videofree > 0))
        .values(func.max(mythtvStorage.videofree)))[0][0]
    stats['myth_storage_vf'].append(("Video free maximum",humanize_bytes(stat)))
    stat = list(session.query(mythtvStorage)
        .filter((mythtvStorage.last_modified > now))
        .filter((mythtvStorage.videofree > 0))
        .values(func.avg(mythtvStorage.videofree)))[0][0]
    stats['myth_storage_vf'].append(("Video free average",humanize_bytes(stat)))
    stat = list(session.query(mythtvStorage)
        .filter((mythtvStorage.last_modified > now))
        .filter((mythtvStorage.videofree > 0))
        .values(func.stddev(mythtvStorage.videofree)))[0][0]
    stats['myth_storage_vf'].append(("Video free standard deviation",humanize_bytes(stat)))
    #------------------------------------------------------------------
    stats['myth_log_crit'] = []
    stat = list(session.query(mythtvLogUrgency)
        .filter((mythtvLogUrgency.last_modified > now))
        .filter((mythtvLogUrgency.crit > -1 ))
        .values(func.min(mythtvLogUrgency.crit)))[0][0]
    stat = ('{0:.4f}'.format(stat)) + "%"
    stats['myth_log_crit'].append(("Critical Logging minimum",stat))
    stat = list(session.query(mythtvLogUrgency)
        .filter((mythtvLogUrgency.last_modified > now))
        .filter((mythtvLogUrgency.crit > -1 ))
        .values(func.max(mythtvLogUrgency.crit)))[0][0]
    stat = ('{0:.4f}'.format(stat)) + "%"
    stats['myth_log_crit'].append(("Critical Logging maximum",stat))
    stat = list(session.query(mythtvLogUrgency)
        .filter((mythtvLogUrgency.last_modified > now))
        .filter((mythtvLogUrgency.crit > -1 ))
        .values(func.avg(mythtvLogUrgency.crit)))[0][0]
    stat = ('{0:.4f}'.format(stat)) + "%"
    stats['myth_log_crit'].append(("Critical Logging average",stat))
    stat = list(session.query(mythtvLogUrgency)
        .filter((mythtvLogUrgency.last_modified > now))
        .filter((mythtvLogUrgency.crit > -1 ))
        .values(func.stddev(mythtvLogUrgency.crit)))[0][0]
    stat = ('{0:.4f}'.format(stat))
    stats['myth_log_crit'].append(("Critical Logging standard deviation ",stat))
    #------------------------------------------------------------------
    stats['myth_log_info'] = []
    stat = list(session.query(mythtvLogUrgency)
        .filter((mythtvLogUrgency.last_modified > now))
        .filter((mythtvLogUrgency.info > -1 ))
        .values(func.min(mythtvLogUrgency.info)))[0][0]
    stat = ('{0:.4f}'.format(stat)) + "%"
    stats['myth_log_info'].append(("Information Logging minimum",stat))
    stat = list(session.query(mythtvLogUrgency)
        .filter((mythtvLogUrgency.last_modified > now))
        .filter((mythtvLogUrgency.info > -1 ))
        .values(func.max(mythtvLogUrgency.info)))[0][0]
    stat = ('{0:.4f}'.format(stat)) + "%"
    stats['myth_log_info'].append(("Information Logging maximum",stat))
    stat = list(session.query(mythtvLogUrgency)
        .filter((mythtvLogUrgency.last_modified > now))
        .filter((mythtvLogUrgency.info > -1 ))
        .values(func.avg(mythtvLogUrgency.info)))[0][0]
    stat = ('{0:.4f}'.format(stat)) + "%"
    stats['myth_log_info'].append(("Information Logging average",stat))
    stat = list(session.query(mythtvLogUrgency)
        .filter((mythtvLogUrgency.last_modified > now))
        .filter((mythtvLogUrgency.info > -1 ))
        .values(func.stddev(mythtvLogUrgency.info)))[0][0]
    stat = ('{0:.4f}'.format(stat))
    stats['myth_log_info'].append(("Information Logging standard deviation ",stat))
    #------------------------------------------------------------------
    stats['myth_log_notice'] = []
    stat = list(session.query(mythtvLogUrgency)
        .filter((mythtvLogUrgency.last_modified > now))
        .filter((mythtvLogUrgency.notice > -1 ))
        .values(func.min(mythtvLogUrgency.notice)))[0][0]
    stat = ('{0:.4f}'.format(stat)) + "%"
    stats['myth_log_notice'].append(("Notice Logging minimum",stat))
    stat = list(session.query(mythtvLogUrgency)
        .filter((mythtvLogUrgency.last_modified > now))
        .filter((mythtvLogUrgency.notice > -1 ))
        .values(func.max(mythtvLogUrgency.notice)))[0][0]
    stat = ('{0:.4f}'.format(stat)) + "%"
    stats['myth_log_notice'].append(("Notice Logging maximum",stat))
    stat = list(session.query(mythtvLogUrgency)
        .filter((mythtvLogUrgency.last_modified > now))
        .filter((mythtvLogUrgency.notice > -1 ))
        .values(func.avg(mythtvLogUrgency.notice)))[0][0]
    stat = ('{0:.4f}'.format(stat)) + "%"
    stats['myth_log_notice'].append(("Notice Logging average",stat))
    stat = list(session.query(mythtvLogUrgency)
        .filter((mythtvLogUrgency.last_modified > now))
        .filter((mythtvLogUrgency.notice > -1 ))
        .values(func.stddev(mythtvLogUrgency.notice)))[0][0]
    stat = ('{0:.4f}'.format(stat))
    stats['myth_log_notice'].append(("Notice Logging standard deviation ",stat))
    #------------------------------------------------------------------
    stats['myth_log_warning'] = []
    stat = list(session.query(mythtvLogUrgency)
        .filter((mythtvLogUrgency.last_modified > now))
        .filter((mythtvLogUrgency.warning > -1 ))
        .values(func.min(mythtvLogUrgency.warning)))[0][0]
    stat = ('{0:.4f}'.format(stat)) + "%"
    stats['myth_log_warning'].append(("Warning Logging minimum",stat))
    stat = list(session.query(mythtvLogUrgency)
        .filter((mythtvLogUrgency.last_modified > now))
        .filter((mythtvLogUrgency.warning > -1 ))
        .values(func.max(mythtvLogUrgency.warning)))[0][0]
    stat = ('{0:.4f}'.format(stat)) + "%"
    stats['myth_log_warning'].append(("Warning Logging maximum",stat))
    stat = list(session.query(mythtvLogUrgency)
        .filter((mythtvLogUrgency.last_modified > now))
        .filter((mythtvLogUrgency.warning > -1 ))
        .values(func.avg(mythtvLogUrgency.warning)))[0][0]
    stat = ('{0:.4f}'.format(stat)) + "%"
    stats['myth_log_warning'].append(("Warning Logging average",stat))
    stat = list(session.query(mythtvLogUrgency)
        .filter((mythtvLogUrgency.last_modified > now))
        .filter((mythtvLogUrgency.warning > -1 ))
        .values(func.stddev(mythtvLogUrgency.warning)))[0][0]
    stat = ('{0:.4f}'.format(stat))
    stats['myth_log_warning'].append(("Warning Logging standard deviation ",stat))
    #------------------------------------------------------------------
    stats['myth_log_err'] = []
    stat = list(session.query(mythtvLogUrgency)
        .filter((mythtvLogUrgency.last_modified > now))
        .filter((mythtvLogUrgency.err > -1 ))
        .values(func.min(mythtvLogUrgency.err)))[0][0]
    stat = ('{0:.4f}'.format(stat)) + "%"
    stats['myth_log_err'].append(("Error Logging minimum",stat))
    stat = list(session.query(mythtvLogUrgency)
        .filter((mythtvLogUrgency.last_modified > now))
        .filter((mythtvLogUrgency.err > -1 ))
        .values(func.max(mythtvLogUrgency.err)))[0][0]
    stat = ('{0:.4f}'.format(stat)) + "%"
    stats['myth_log_err'].append(("Error Logging maximum",stat))
    stat = list(session.query(mythtvLogUrgency)
        .filter((mythtvLogUrgency.last_modified > now))
        .filter((mythtvLogUrgency.err > -1 ))
        .values(func.avg(mythtvLogUrgency.err)))[0][0]
    stat = ('{0:.4f}'.format(stat)) + "%"
    stats['myth_log_err'].append(("Error Logging average",stat))
    stat = list(session.query(mythtvLogUrgency)
        .filter((mythtvLogUrgency.last_modified > now))
        .filter((mythtvLogUrgency.err > -1 ))
        .values(func.stddev(mythtvLogUrgency.err)))[0][0]
    stat = ('{0:.4f}'.format(stat))
    stats['myth_log_err'].append(("Error Logging standard deviation ",stat))
    #------------------------------------------------------------------
    mythuuid = select([func.count(mythtv_host.c.myth_uuid).label('cnt')],
                        order_by=[desc('cnt')],
                        group_by=[mythtv_host.c.myth_uuid]).where(mythtv_host.c.last_modified > now).execute().fetchall()

    item_count={}
    for itemt in mythuuid:
        item=itemt[0]
        if item in item_count:
            item_count[item] = item_count[item] + 1
        else:
            item_count[item] = 1

    stats['myth_cluster'] = item_count

    stats['myth_snd'] = handle_withheld_elem(
            session.query(MythSnd).all(),
            'audio_sys', WITHHELD_MAGIC_STRING)

    stats['myth_remote'] = handle_withheld_elem(
            session.query(MythRemote).all(),
            'remote', WITHHELD_MAGIC_STRING)

    stats['myth_type'] = handle_withheld_elem(
            session.query(MythType).all(),
            'myth_type', WITHHELD_MAGIC_STRING)
    #------------------------------------------------------------------
    # total tuners breakdown
    myth_global_tuner_count = select( [
                func.sum(mythtv_tuners.c.tuner_count).label('cnt')],
                order_by=[desc('cnt')]).where(mythtv_tuners.c.last_modified > now).execute().fetchall()

    stats['myth_t_count'] = myth_global_tuner_count[0][0]

    myth_global_tuner = select( [mythtv_tuners.c.tuner_type,
                func.sum(mythtv_tuners.c.tuner_count).label('cnt')],
                order_by=[desc('cnt')],
                group_by=[ mythtv_tuners.c.tuner_type ]).where(mythtv_tuners.c.last_modified > now).execute().fetchall()
    stats['myth_global_tuner'] = myth_global_tuner
    #------------------------------------------------------------------
    #vt per cluster
    # This query uses a subquery because of the group by clause.
    sub_query = (session.query(func.sum(mythtvHost.vtpertuner).label('b'))
            .filter((mythtvHost.last_modified > now))
            .filter((mythtvHost.vtpertuner > -1 ))
            .group_by((mythtvHost.myth_uuid)))

    stats['myth_vtuner_cluster'] = []
    stat = session.query(func.min(sub_query.subquery().columns.b)).scalar()
    stat = ('{0:.4f}'.format(stat))
    stats['myth_vtuner_cluster'].append(("Virtual Tuner minimum",stat))

    stat = session.query(func.max(sub_query.subquery().columns.b)).scalar()
    stat = ('{0:.4f}'.format(stat))
    stats['myth_vtuner_cluster'].append(("Virtual Tuner maximum",stat))

    stat = session.query(func.avg(sub_query.subquery().columns.b)).scalar()
    stat = ('{0:.4f}'.format(stat))
    stats['myth_vtuner_cluster'].append(("Virtual Tuner average",stat))

    stat = session.query(func.stddev(sub_query.subquery().columns.b)).scalar()
    stat = ('{0:.4f}'.format(stat))
    stats['myth_vtuner_cluster'].append(("Virtual Tuner standard deviation ",stat))

    #------------------------------------------------------------------
    #tuners per cluster
    stats['myth_tuner_cluster'] = []
    sub_query = (session.query(func.sum(mythtvtuners.tuner_count).label('b'))
            .filter((mythtvtuners.last_modified > now))
            .filter((mythtvtuners.tuner_count > -1 ))
            .group_by((mythtvtuners.myth_uuid)))
    stat = session.query(func.min(sub_query.subquery().columns.b)).scalar()
    stat = ('{0:.4f}'.format(stat))
    stats['myth_tuner_cluster'].append(("Cluster Tuner minimum",stat))

    stat = session.query(func.max(sub_query.subquery().columns.b)).scalar()
    stat = ('{0:.4f}'.format(stat))
    stats['myth_tuner_cluster'].append(("Cluster Tuner maximum",stat))

    stat = session.query(func.avg(sub_query.subquery().columns.b)).scalar()
    stat = ('{0:.4f}'.format(stat))
    stats['myth_tuner_cluster'].append(("Cluster Tuner average",stat))

    stat = session.query(func.stddev(sub_query.subquery().columns.b)).scalar()
    stat = ('{0:.4f}'.format(stat))
    stats['myth_tuner_cluster'].append(("Cluster Tuner standard deviation ",stat))

    return stats
