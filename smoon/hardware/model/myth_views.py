# -*- coding: utf-8 -*-
from views import *
myth_import_string="from myth_views import MythRole, myth_role,\
                                           MythRemote, myth_remote,\
                                           MythTheme, myth_theme,\
                                           MythPlugins, myth_plugins,\
                                           MythTuner, myth_tuner"

class MythRole(object):
    pass
class MythRemote(object):
    pass
class MythTheme(object):
    pass
class MythPlugins(object):
    pass
class MythTuner(object):
    pass

myth_role = simple_mapped_counted_view('MYTH_SYSTEMROLE', old_hosts.c.myth_role,
                                              MythRole, desc=True)

myth_remote = simple_mapped_counted_view('MYTH_REMOTE', old_hosts.c.myth_remote,
                                         MythRemote, desc=True)

myth_theme = simple_mapped_counted_view('MYTHTHEME', old_hosts.c.myth_theme,
                                        MythTheme, desc=True)

myth_plugins = simple_mapped_counted_view('MYTH_PLUGINS', old_hosts.c.myth_plugins,
                                        MythPlugins, desc=True)

myth_tuner = simple_mapped_counted_view('MYTHTTUNER', old_hosts.c.myth_tuner,
                                        MythTuner, desc=True)

