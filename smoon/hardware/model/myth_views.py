
# -*- coding: utf-8 -*-
from views import *
from hardware.model.model_mythtv import *


myth_import_string="from hardware.model.myth_views import  \
                                           MythTheme, myth_theme, \
                                           MythLanguage, myth_language, \
                                           MythTimezone, myth_timezone, \
                                           MythVersion, myth_version, \
                                           MythSourceCount, myth_sourcecount, \
                                           MythDbVersion, myth_dbversion, \
                                           MythQTVersion, myth_qtversion, \
                                           MythBranch, myth_branch, \
                                           MythGrabber, myth_grabbers, \
                                           MythSnd, myth_snd, \
                                           MythRemote, myth_remote, \
                                           MythType, myth_type, \
                                           MythCountry, myth_country \
                                           "


def old_myth_hosts_clause(tablename):
    string = (tablename.c.last_modified > (date.today() - timedelta(days=90)))
    return string

def old_myth_hosts_table(tablename):
    return select([tablename], old_myth_hosts_clause(tablename)).alias('old_myth_hosts')

def old_myth_hosts(tablename):
    rc = old_myth_hosts_table(tablename)
    return rc

class MythLanguage(object):
    pass

class MythTheme(object):
    pass

class MythTimezone(object):
    pass

class MythVersion(object):
    pass

class MythSourceCount(object):
    pass

class MythDbVersion(object):
    pass

class MythQTVersion(object):
    pass

class MythBranch(object):
    pass

class MythGrabber(object):
    pass

class MythSnd(object):
    pass

class MythRemote(object):
    pass

class MythType(object):
    pass

class MythCountry(object):
    pass


myth_language = simple_mapped_counted_view('MYTH_LANGUAGE',old_myth_hosts(mythtv_host).c.language,
                                         MythLanguage, desc=True)

myth_theme = simple_mapped_counted_view('MYTH_THEME',old_myth_hosts(mythtv_host).c.theme,
                                         MythTheme, desc=True)

myth_timezone = simple_mapped_counted_view('MYTH_TIMEZONE',old_myth_hosts(mythtv_host).c.timezone,
                                         MythTimezone, desc=True)

myth_version = simple_mapped_counted_view('MYTH_VERSION',old_myth_hosts(mythtv_host).c.myth_version_bucket,
                                         MythVersion, desc=True)

myth_sourcecount = simple_mapped_counted_view('MYTH_SOURCECOUNT',
                                               old_myth_hosts(mythtv_host).c.sourcecount,
                                               MythSourceCount, desc=True)

myth_dbversion  =  simple_mapped_counted_view('MYTH_DBVERSION',
                                               old_myth_hosts(mythtv_database).c.version,
                                               MythDbVersion, desc=True)

myth_qtversion = simple_mapped_counted_view('MYTH_QTVERSION',
                                            old_myth_hosts(mythtv_host).c.qt_version,
                                            MythQTVersion, desc=True)

myth_branch  =  simple_mapped_counted_view('MYTH_BRANCH',
                                               old_myth_hosts(mythtv_host).c.branch,
                                               MythBranch, desc=True)


myth_grabbers  =  simple_mapped_counted_view('MYTH_GRABBER',
                                               old_myth_hosts(mythtv_grabbers).c.grabber,
                                               MythGrabber, desc=True)


myth_snd  =  simple_mapped_counted_view('MYTH_SND',
                old_myth_hosts(mythtv_audio).c.audio_sys, MythSnd, desc=True)

myth_remote = simple_mapped_counted_view('MYTH_REMOTE',
                old_myth_hosts(mythtv_host).c.remote, MythRemote, desc=True)

myth_type = simple_mapped_counted_view('MYTH_TYPE',
                old_myth_hosts(mythtv_host).c.myth_type, MythType, desc=True)


myth_country = simple_mapped_counted_view('MYTH_COUNTRY',old_myth_hosts(mythtv_host).c.country,
                                         MythCountry, desc=True)


       