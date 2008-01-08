from cherrypy import request, response
from turbogears import controllers, expose, identity
from turbogears import exception_handler
from turbogears import redirect

from hardware.controllers.client import Client
from hardware.controllers.token import Token
from hardware.controllers.error import error

import logging
log = logging.getLogger("smoon")

# This is such a bad idea, yet here it is.
CRYPTPASS = 'PleaseChangeMe11'
current_smolt_protocol = '0.97' 


class Root(controllers.RootController):
    tokens = Token(current_smolt_protocol, CRYPTPASS) #should be 'token' but it is taken :(
    client = Client(current_smolt_protocol, tokens)
    error = error
    
    def __init__(self):
        controllers.RootController.__init__(self)
            
    #legacy definitions
    #TODO wrap these things into counters to measure current
    #usage patterns
    show = client.show
    show_all = client.show_all
#    share = client.share
    delete = client.delete
    add = client.add
    addDevices = client.add_devices
    add_json = client.add_json
    rate_object = client.rate_object
    
    token = tokens.token
    token_json = tokens.token_json
    check_token = tokens.check_token
    
    error_web = error.error_web
    error_client = error.error_client

        
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

    @expose(template="hardware.templates.my_hosts")
    @identity.require(identity.not_anonymous())
    def my_hosts(self):
        try:
            link_sql = ctx.current.query(FasLink).selectone_by(user_name=identity.current.user_name)
        except InvalidRequestError:
            link_sql = []
        return dict(link_sql=link_sql)

    @expose(template="hardware.templates.link")
    @identity.require(identity.not_anonymous())
    def link(self, UUID):
        try:
            host_sql = ctx.current.query(Host).selectone_by(uuid=UUID)
        except InvalidRequestError:
            raise ValueError("Critical: Your UUID did not exist.")
        
        if host_sql.fas_account == None:
            link_sql = FasLink(uuid=UUID, user_name=identity.current.user_name)
            ctx.current.flush()
        return dict()
    
    @expose(template="hardware.templates.not_loaded")
    def unavailable(self, tg_exceptions=None):
        return dict()
        
