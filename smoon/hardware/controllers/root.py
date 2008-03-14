from cherrypy import request, response
from turbogears import controllers, expose, identity
from turbogears import exception_handler
from turbogears import redirect
from turbogears import config
import turbogears

from hardware.controllers.client import Client
from hardware.controllers.token import Token
from hardware.controllers.upgrade import Upgrade
from hardware.controllers.error import error
from hardware.controllers.reports import Reports
from hardware.turboflot import TurboFlot

from hardware.model import *

import logging
log = logging.getLogger("smoon")

from turbogears.i18n import gettext
from genshi.filters import Translator
import turbogears.startup
import turbogears.view

def genshi_loader_callback(template):
    template.filters.insert(0, Translator(gettext))

def init_callback():
    turbogears.view.engines['genshi'].loader.callback = genshi_loader_callback

turbogears.startup.call_on_startup.append( init_callback )
config.update({'genshi.loader_callback': genshi_loader_callback})

# This is such a bad idea, yet here it is.
CRYPTPASS = 'PleaseChangeMe11'
current_smolt_protocol = '0.97' 

class Root(controllers.RootController):
    tokens = Token(current_smolt_protocol, CRYPTPASS) #should be 'token' but it is taken :(
    client = Client(current_smolt_protocol, tokens)
    upgrade = Upgrade()
    reports = Reports()
    error = error
    
    def __init__(self):
        controllers.RootController.__init__(self)
        
    @expose(template="hardware.templates.welcome")
    def index(self):
        import time
        # log.debug("Happy TurboGears Controller Smooning For Duty")
        import math
        from turboflot import TurboFlot
        #archs = session.query(Arch).select()
        topVendors = session.query(Host).group_by(Host.vendor).filter_by(rating=5).add_column(func.count(Host.rating).label('count')).order_by(desc('count')).limit(7)
        types = []
        count = []
        i = 1
        vendors = []
        counts = []
        for vend in topVendors:
            vendors.append([i + .5, vend[0].vendor])
            counts.append([i, vend[1]])
            i = i + 1
        vendorFlot = TurboFlot([
            {
                'data' : counts,
                'bars' : { 'show' : True },
                'label' : 'Vendors',
            }],
            {
                'xaxis' : { 'ticks' : vendors },
            }
        )
        return dict(now=time.ctime(), vendorFlot=vendorFlot)
        
    @exception_handler(error.error_web,rules="isinstance(tg_exceptions,ValueError)")
    @expose(template="hardware.templates.token", allow_json=True)
    def token(self, UUID):
        raise ValueError("Critical: Unicode Issue - Tell Mike!")


    @expose(template="hardware.templates.login")
    def login(self, forward_url=None, previous_url=None, *args, **kw):

        if not identity.current.anonymous \
            and identity.was_login_attempted() \
            and not identity.get_identity_errors():
            raise redirect(forward_url)

        forward_url=None
        previous_url= request.path

        if identity.was_login_attempted():
            msg=_("The credentials you supplied were not correct or "
                   "did not grant access to this resource.")
        elif identity.get_identity_errors():
            msg=_("You must provide your credentials before accessing "
                   "this resource.")
        else:
            msg=_("Please log in.")
            forward_url= request.headers.get("Referer", "/")

        response.status=403
        return dict(message=msg, previous_url=previous_url, logging_in=True,
                    original_parameters=request.params,
                    forward_url=forward_url)


    @expose()
    def time(self):
        import time
        return time.ctime()
