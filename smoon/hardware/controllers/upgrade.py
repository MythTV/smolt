from hardware.model import *
from turbogears import expose

class UUIDError(Exception):
    pass


def generate_uuid(public=False):
    try:
        uuid = file('/proc/sys/kernel/random/uuid').read().strip()
        if public:
            uuid = "pub_" + uuid
        return uuid
    except IOError:
        raise UUIDError("Cannot generate UUID")


class Upgrade(object):
    def __init__(self):
        pass
    @expose()
    def upgrade(self):
        for host in ctx.current.query(Host).filter_by(pub_uuid="").limit(1000):
            host.pub_uuid=generate_uuid(True)
            ctx.current.flush()
#        for host in ctx.current.query(Host):
#            #if host.pub_uuid
#            pass
        return dict()