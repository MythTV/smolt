# -*- coding: utf-8 -*-
from turbogears import expose
from hardware.model import *
from sqlalchemy.sql import *
from turbogears.database import session

#I think that we'll need a way to attach meta data to our tables
#to define how different fields can be search from.
#from a design standpoint, it's interesting which layer it goes on
#but for now, we'll cobble it out with duct tape and elmers glue
hosts_ban = ['id', 'uuid', 'pub_uuid', 'last_modified', 'bogomips']

class Reports(object):
    @expose()
    def index(self):
        return self.search()

    @expose(template='hardware.templates.report_recent')
    def recent(self):
        ''' Shows recently added hosts and devices '''
        recent_pub_uuid = select([Host.pub_uuid, Host.last_modified],
              Host.last_modified > (date.today() - timedelta(days=90)))\
              .order_by(desc(Host.last_modified)).limit(20).execute()\
              .fetchall()
        recent_devices = select([computer_logical_devices.c.description,
                          computer_logical_devices.c.date_added],
                          computer_logical_devices.c.date_added > (date.today() -
                          timedelta(days=90))).order_by(desc(computer_logical_devices\
                          .c.date_added)).limit(50).execute().fetchall()
        return dict(recent_pub_uuid=recent_pub_uuid,
                    recent_devices=recent_devices)

    @expose(template='hardware.templates.report_host_ratings')
    def host_ratings(self):
      ''' Return basic ratings information '''
      host_ratings = select([Host.system, Host.vendor, Host.rating,
        func.count(Host.rating)], Host.rating != 0).group_by(Host.system).\
        order_by(desc(func.count(Host.rating))).limit(50).\
        execute().fetchall()
#      This query is for the last 90 days.
#      host_ratings = select([Host.system, Host.vendor, Host.rating,
#        func.count(Host.rating)],  and_(Host.last_modified > (date.today() -
#        timedelta(days=90)), Host.rating != 0)).group_by(Host.system).\
#        order_by(desc(func.count(Host.rating))).limit(50).\
#        execute().fetchall()
      return dict(host_ratings=host_ratings)

    @expose(template='hardware.templates.report_device_ratings')
    def device_ratings(self):
      ''' Return basic ratings information '''
      h = select([HostLink.device_id, HostLink.rating,
          func.count(HostLink.rating).label('cnt')], HostLink.rating != 0).\
          group_by(HostLink.device_id, HostLink.rating).\
          order_by(desc('cnt')).limit(500).alias('h')
      device_ratings = select([ComputerLogicalDevice.description, h.c.rating, h.c.cnt], ComputerLogicalDevice.id==h.c.device_id).execute().fetchall()
      return dict(device_ratings=device_ratings)

    @expose(template='hardware.templates.report_search_profiles')
    def search_profiles(self):
        return dict()

    @expose(template='hardware.templates.report_view_profiles')
    def view_profiles(self, profile, not_rated=6, *args, **keys):
        found = select([Host.system, Host.vendor, Host.rating,
                func.count(Host.rating)], and_(Host.rating != not_rated,
                or_(Host.system.like('''%%%s%%''' % profile), Host.vendor.\
                like('''%%%s%%''' % profile)))).group_by(Host.rating,
                Host.system, Host.vendor).order_by(desc(\
                func.count(Host.rating))).limit(500).execute().fetchall()
        return dict(found=found)

    @expose(template='hardware.templates.report_view_profile')
    def view_profile(self, profile, not_rated=6, *args, **keys):
        found = select([Host.system, Host.vendor, Host.rating,
                func.count(Host.rating)], and_(Host.rating != not_rated,
                or_(Host.system.like('''%%%s%%''' % profile), Host.vendor.\
                like('''%%%s%%''' % profile)))).group_by(Host.rating,
                Host.system, Host.vendor).order_by(desc(\
                func.count(Host.rating))).limit(500).execute().fetchall()
        pub_uuids = select([Host.pub_uuid, Host.rating], and_(Host.pub_uuid!='', or_(Host.system.like('''%%%s%%''' % profile), Host.vendor.\
                like('''%%%s%%''' % profile)))).limit(500).execute().fetchall()
        return dict(found=found, pub_uuids=pub_uuids)

    @expose(template='hardware.templates.report_search_devices')
    def search_devices(self):
        return dict()

    @expose(template='hardware.templates.report_view_devices')
    def view_devices(self, *args, **keys):
        device = keys['device']
#        d = select([ComputerLogicalDevice.id, ComputerLogicalDevice.description],
#            ComputerLogicalDevice.description.like('''%%%s%%''' % device)).limit(1000).alias('d')
#        found = select ([HostLink.rating, func.count(HostLink.rating).label('cnt'),
#            d.c.description], HostLink.device_id == d.c.id).group_by(HostLink.rating,
#            d.c.description).order_by(desc('cnt')).execute().fetchall()
        session.bind = metadata.bind
        found = session.execute('''SELECT host_links.rating, count(host_links.rating) AS cnt, d.description, d.vendor_id, d.device_id, d.subsys_vendor_id, d.subsys_device_id FROM host_links use index(rating), (SELECT device.id AS id, device.vendor_id AS vendor_id, device.device_id AS device_id, device.subsys_vendor_id AS subsys_vendor_id, device.subsys_device_id AS subsys_device_id, device.description AS description FROM device WHERE device.description like '%%%%%s%%%%'  LIMIT 500) AS d WHERE host_links.device_id = d.id and host_links.rating != 0 GROUP BY host_links.rating, d.description, d.vendor_id, d.device_id, d.subsys_vendor_id, d.subsys_device_id ORDER BY cnt DESC;''' % device).fetchall()
        return dict(found=found)

    @expose(template='hardware.templates.report_view_device')
    def view_device(self, device, *args, **keys):
#        d = select([ComputerLogicalDevice.id, ComputerLogicalDevice.vendor_id, ComputerLogicalDevice.device_id, ComputerLogicalDevice.subsys_vendor_id, ComputerLogicalDevice.subsys_device_id, ComputerLogicalDevice.description],
#            ComputerLogicalDevice.description == '''%s''' % device).limit(1000).alias('d')
#        found = select ([HostLink.rating, func.count(HostLink.rating).label('cnt'),
#            d.c.description, d.c.vendor_id, d.c.device_id, d.c.subsys_vendor_id, d.c.subsys_device_id], HostLink.device_id == d.c.id).group_by(HostLink.rating,
#            d.c.description, d.c.vendor_id, d.c.device_id, d.c.subsys_vendor_id, d.c.subsys_device_id).order_by(desc('cnt')).execute().fetchall()

        session.bind = metadata.bind

        found = session.execute('''SELECT host_links.rating, count(host_links.rating) AS cnt, d.description, d.vendor_id, d.device_id, d.subsys_vendor_id, d.subsys_device_id FROM host_links use index(rating), (SELECT device.id AS id, device.vendor_id AS vendor_id, device.device_id AS device_id, device.subsys_vendor_id AS subsys_vendor_id, device.subsys_device_id AS subsys_device_id, device.description AS description FROM device WHERE device.description = '%s'  LIMIT 500) AS d WHERE host_links.device_id = d.id and host_links.rating != 0 GROUP BY host_links.rating, d.description, d.vendor_id, d.device_id, d.subsys_vendor_id, d.subsys_device_id ORDER BY cnt DESC;''' % device).fetchall()
            # Select Device ID's that match our description
        d = select([computer_logical_devices.c.id],
                computer_logical_devices.c.description == device).alias('d')

            # Select the host ID's that have our device ID (from description)
        hl = select([HostLink.host_link_id],
             HostLink.device_id==d.c.id).limit(1000).alias('hl')

            # Select pub_uuids that match our host ID from device ID from desc)
        profiles = select([distinct(Host.pub_uuid), Host.system, Host.vendor], Host.id == hl.c.host_link_id).execute().fetchall()
        device = args
        return dict(found=found, profiles=profiles, device=device)


    @expose(template='hardware.templates.report_search')
    def search(self):
        host_cols = [col.name for col in hosts.c]
        host_cols = filter(lambda x: x not in hosts_ban, host_cols)
        return dict(fields=host_cols)

    @expose(template='hardware.templates.report_view')
    def view(self, *args, **keys):
        restrict = keys['restrict_field']
        restrict_vals = keys['table_values']
        to_count = keys['count_field']
        limit_col = getattr(hosts.c, restrict)
        print restrict_vals
        def cmp_up(a):
            return limit_col==a
        restrict_clause = reduce(or_, map(cmp_up, restrict_vals))
        print restrict_clause
        temp_host = select([hosts], restrict_clause).alias('tmp_host')
        view = simple_counted_view('tmp', getattr(temp_host.c, to_count),
                                   desc=True)
        data = just_select(view)
        total = just_count(temp_host)
        return dict(results=data, total=total, name=to_count, 
                    restrict=restrict, restrict_vals=restrict_vals)
    
    @expose('json')
    def values_for_column(self, *args, **keys):
        col_name = keys['col_name']
        col = getattr(hosts.c, col_name)
        vals = select([func.distinct(col)]).order_by(col).execute().fetchall()
        vals = [val[0] for val in vals]
        return dict(values=vals)
