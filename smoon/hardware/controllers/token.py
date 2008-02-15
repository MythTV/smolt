from Crypto.Cipher import XOR
import urllib
import time
from datetime import datetime

from turbogears import expose

class Token(object):
    def __init__(self, smolt_protocol, password):
        self.smolt_protocol = smolt_protocol
        self.password = password
        
    @expose(template="hardware.templates.token", allow_json=True)
    def token(self, uuid):
        crypt = XOR.new(self.password)
        str = "%s\n%s " % ( int(time.mktime(datetime.now().timetuple())), uuid)
        # I hate obfuscation.  Its all I've got
        token = crypt.encrypt(str)
        return dict(token=urllib.quote(token),
                    prefered_protocol=".91")

    @expose("json")
    def token_json(self, uuid):
        crypt = XOR.new(self.password)
        str = "%s\n%s " % ( int(time.mktime(datetime.now().timetuple())), uuid)
        # I hate obfuscation.  Its all I've got
        token = crypt.encrypt(str)
        return dict(token=urllib.quote(token),
                    prefered_protocol=self.smolt_protocol)
        
    @expose("json")
    def admin_token_json(self, uuid):
        from hardware.model import *
        crypt = XOR.new(self.password)
        try:
            host_object = ctx.current.query(Host).selectone_by(uuid=uuid)
        except:
            raise ValueError("Critical: UUID Not Found - %s" % uuid)
        
        str = "%s" % (uuid[:7])
        # I hate obfuscation.  Its all I've got
        token = crypt.encrypt(str)
        return dict(token=urllib.quote(token),
                    prefered_protocol=self.smolt_protocol)
        
    def check_token(self, token, uuid):
        token = urllib.unquote(token)
        crypt = XOR.new(self.password)
        token_plain = crypt.decrypt(token).split('\n')
        token_time = int(token_plain[0])
        token_uuid = token_plain[1]
        current_time = int(time.mktime(datetime.now().timetuple()))
        if current_time - token_time > 20:
            raise ValueError("Critical [20]: Invalid Token")
        if uuid.strip() != token_uuid.strip():
            raise ValueError("Critical [s]: Invalid Token")
    
    def check_admin_token(self, token, uuid):
        print "TOKEN CHECK"
        token = urllib.unquote(token)
        crypt = XOR.new(self.password)
        token_plain = crypt.decrypt(token).split('\n')
        if uuid[:7] == token_plain[0]:
            print 'GOT GOOD TOKEN!'
            return token
        else:
            raise ValueError("Critical: %s not a valid token for UUID" % token)
