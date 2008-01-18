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
