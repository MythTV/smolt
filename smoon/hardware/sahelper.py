#This module is inherently deprecated
#It is being created to do some weird hacks in SA that are
#thrown up because of the odd transition TG is going
#through in switching over.
#When Smoon transitions to 0.4, this will not be necessary
import sqlalchemy
from sqlalchemy.ext import activemapper, sessioncontext
from sqlalchemy.ext.sessioncontext import SessionContext
from sqlalchemy.orm.mapper import global_extensions
from turbogears import config
from turbogears.database import metadata

_engine = None

def get_engine():
    "Retreives the engine based on the current configuration"
    global _engine
    if not _engine:
        alch_args = dict()
        for k, v in config.config.configMap["global"].items():
            if "sqlalchemy" in k:
                alch_args[k.split(".")[-1]] = v
        dburi = alch_args.pop('dburi')
        if not dburi:
            raise KeyError("No sqlalchemy database config found!")
        _engine = sqlalchemy.create_engine(dburi, **alch_args)
        metadata.connect(_engine)
    elif not metadata.is_bound():
        metadata.connect(_engine)
    return _engine

def create_session():
    "Creates a session with the appropriate engine"
    return sqlalchemy.create_session(bind_to=get_engine())

ctx = SessionContext(lambda:sqlalchemy.create_session(bind_to=get_engine()))

global_extensions.append(ctx.mapper_extension)

__all__ = ['ctx']
