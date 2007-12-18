from turbogears import expose

class Error(object):
    @expose(template="hardware.templates.error")
    def error_client(self, tg_exceptions=None, *args, **keys):
        ''' Exception handler, Sends messages back to the client'''
        message = 'ServerMessage: %s' % tg_exceptions
        return dict(handling_value=True,exception=message)

    @expose(template="hardware.templates.error")
    def error_web(self, tg_exceptions=None, *args, **keys):
        ''' Exception handler, Sends messages back to the client'''
        message = 'Error: %s' % tg_exceptions
        return dict(handling_value=True,exception=message)

error = Error()
