from turbogears import expose

class Error(object):
    @expose(template="hardware.templates.error")
    def error_client(self, *args, **keys):
        ''' Exception handler, Sends messages back to the client'''
        message = 'ServerMessage: %s' % keys['tg_exceptions']
        return dict(handling_value=True,exception=message)

    @expose(template="hardware.templates.error")
    def error_web(self, *args, **keys):
        ''' Exception handler, Sends messages back to the client'''
        message = 'Error: %s' % keys['tg_exceptions']
        return dict(handling_value=True,exception=message)

error = Error()
