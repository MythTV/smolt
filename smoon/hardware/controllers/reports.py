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