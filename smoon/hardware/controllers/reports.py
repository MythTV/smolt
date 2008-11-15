from turbogears import expose
from hardware.model import *
from sqlalchemy.sql import *

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
        recent_pub_uuid = select([Host.c.pub_uuid, Host.c.last_modified],
              Host.c.last_modified > (date.today() - timedelta(days=90)))\
              .order_by(desc(Host.c.last_modified)).limit(20).execute()\
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
      host_ratings = select([Host.c.system, Host.c.vendor, Host.c.rating,
        func.count(Host.c.rating)], Host.c.rating != 0).group_by(Host.c.system).\
        order_by(desc(func.count(Host.c.rating))).limit(50).\
        execute().fetchall()
#      This query is for the last 90 days.
#      host_ratings = select([Host.c.system, Host.c.vendor, Host.c.rating,
#        func.count(Host.c.rating)],  and_(Host.c.last_modified > (date.today() -
#        timedelta(days=90)), Host.c.rating != 0)).group_by(Host.c.system).\
#        order_by(desc(func.count(Host.c.rating))).limit(50).\
#        execute().fetchall()
      return dict(host_ratings=host_ratings)

    @expose(template='hardware.templates.report_device_ratings')
    def device_ratings(self):
      ''' Return basic ratings information '''
      h = select([HostLink.c.device_id, HostLink.c.rating,
          func.count(HostLink.c.rating).label('cnt')], HostLink.c.rating != 0).\
          group_by(HostLink.c.device_id, HostLink.c.rating).\
          order_by(desc('cnt')).limit(500).alias('h')
      device_ratings = select([ComputerLogicalDevice.c.description, h.c.rating, h.c.cnt], ComputerLogicalDevice.c.id==h.c.device_id).execute().fetchall()
      return dict(device_ratings=device_ratings)

    @expose(template='hardware.templates.report_search_devices')
    def search_devices(self):
        host_cols = [col.name for col in hosts.c]
        host_cols = filter(lambda x: x not in hosts_ban, host_cols)
        return dict(fields=host_cols)

    @expose(template='hardware.templates.report_view_devices')
    def view_devices(self, *args, **keys):
        device = keys['device']
        d = select([ComputerLogicalDevice.c.id, ComputerLogicalDevice.c.description],
            ComputerLogicalDevice.c.description.like('''%%%s%%''' % device)).limit(1000).alias('d')
        found = select ([HostLink.c.rating, func.count(HostLink.c.rating).label('cnt'),
            d.c.description], HostLink.c.device_id == d.c.id).group_by(HostLink.c.rating,
            d.c.description).order_by(desc('cnt')).execute().fetchall()
        return dict(found=found)

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