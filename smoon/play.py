# =========================================================
# Config
# =========================================================
CONNECTION = 'mysql://smoon:smoon@localhost/smoon'
ECHO=True
#ECHO=False
#DROP=True
DROP=False
machine_id = 3

# =========================================================
# Imports
# =========================================================
import sqlalchemy
print sqlalchemy.__version__
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, eagerload
from playmodel import *

# =========================================================
# Setup
# =========================================================
engine = create_engine(CONNECTION, echo=ECHO)
session = sessionmaker(bind=engine)()

if DROP:
    metadata.drop_all(engine)
metadata.create_all(engine)

# Gather old and new data
import sys
import os
sys.path.append(os.path.join(sys.path[0], '..', 'client', 'distros'))
sys.path.append(os.path.join(sys.path[0], '..', 'client'))
from gentoo.globaluseflags import GlobalUseFlags
current_global_use_flags = GlobalUseFlags().serialize() + ['foo', 'FFFFFFF', 'AAAAAAA', 'XXX', 'JJJJJJ']
old_global_use_flag_objects = session.query(GentooGlobalUseFlag).options(eagerload('use_flag')).filter_by(machine_id=machine_id).all()

# Calculate diff
old_set = set(e.use_flag.name for e in old_global_use_flag_objects)  # EAGERLOAD for this line
current_set = set(current_global_use_flags)
flags_to_add = current_set - old_set
flags_to_remove = old_set - current_set

# Apply diff
for i in flags_to_add:
    try:
        flag_object = session.query(GentooUseFlagString).filter_by(name=i).one()
    except sqlalchemy.orm.exc.NoResultFound:
        flag_object = GentooUseFlagString(i)
        session.add(flag_object)
        session.flush()
    print 'ADD', flag_object.name
    session.add(GentooGlobalUseFlag(machine_id, flag_object.id))
for flag_object in old_global_use_flag_objects:
    name = flag_object.use_flag.name
    if name in flags_to_remove:
        print 'DEL', name
        session.delete(flag_object)
session.flush()
