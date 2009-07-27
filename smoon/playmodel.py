from sqlalchemy import Table, Column, Integer, CHAR, ForeignKey, UniqueConstraint, MetaData
from sqlalchemy.orm import mapper, relation
metadata = MetaData()

# =========================================================
# gentoo_use_flag_pool
# =========================================================
_gentoo_use_flag_pool_table = Table('gentoo_use_flag_pool', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', CHAR(255), unique=True),
)

class GentooUseFlagString(object):
    def __init__(self, name):
        self.name = name

mapper(GentooUseFlagString, _gentoo_use_flag_pool_table)


# =========================================================
# gentoo_global_use_flags
# =========================================================
_gentoo_global_use_flags_table = Table('gentoo_global_use_flags', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('machine_id', Integer),
    Column('use_flag_id', Integer, ForeignKey('gentoo_use_flag_pool.id')),
    UniqueConstraint('machine_id', 'use_flag_id'),
)

class GentooGlobalUseFlag(object):
    def __init__(self, machine_id, use_flag_id):
        self.machine_id = machine_id
        self.use_flag_id = use_flag_id

mapper(GentooGlobalUseFlag, _gentoo_global_use_flags_table,
    properties={
        'use_flag':relation(GentooUseFlagString),
    }
)
