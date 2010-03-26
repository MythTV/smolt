# -*- coding: utf-8 -*-
#add the myth stuff to the host_dict
def add_to_host_sql(host_sql,host_dict):

    myth_host_sql = host_sql
    try:
        myth_host_sql.myth_role = host_dict['myth_role']
    except KeyError:
        myth_host_sql.myth_role = 'Unknown'

    try:
        myth_host_sql.myth_remote = host_dict['myth_remote']
    except KeyError:
         myth_host_sql.myth_remote = 'Unknown'

    try:
         myth_host_sql.myth_theme = host_dict['myth_theme']
    except KeyError:
         myth_host_sql.myth_theme = 'Unknown'

    try:
         myth_host_sql.myth_plugins = host_dict['myth_plugins']
    except KeyError:
         myth_host_sql.myth_plugins = 'Unknown'

    try:
         myth_host_sql.myth_tuner = host_dict['myth_tuner']
    except KeyError:
         myth_host_sql.myth_theme = 'Unknown'

    return myth_host_sql
