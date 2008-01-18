from cherrypy import request, response
from turbogears import controllers, expose, identity
from turbogears import exception_handler
from turbogears import redirect

from hardware.controllers.client import Client
from hardware.controllers.token import Token
from hardware.controllers.upgrade import Upgrade
from hardware.controllers.error import error

import logging
log = logging.getLogger("smoon")

# This is such a bad idea, yet here it is.
CRYPTPASS = 'PleaseChangeMe11'
current_smolt_protocol = '0.97' 


class Root(controllers.RootController):
    tokens = Token(current_smolt_protocol, CRYPTPASS) #should be 'token' but it is taken :(
    client = Client(current_smolt_protocol, tokens)
    upgrade = Upgrade()
    error = error
    
    def __init__(self):
        controllers.RootController.__init__(self)
            
        
    @expose(template="hardware.templates.welcome")
    def index(self):
        import time
        # log.debug("Happy TurboGears Controller Smooning For Duty")
        return dict(now=time.ctime())


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
