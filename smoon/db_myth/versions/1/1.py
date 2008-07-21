from sqlalchemy import Table, INT, TEXT, DECIMAL, DATETIME, VARCHAR, BOOLEAN, MetaData, Column, String
from migrate import migrate_engine
from migrate.changeset import create_column, drop_column

meta = MetaData(migrate_engine)
hosts = Table('host', meta,
              Column("id", INT,
                     autoincrement=True,
                     nullable=False,
                     primary_key=True),
              Column('uuid', VARCHAR(36),
                     nullable=False,
                     unique=True),
              Column('pub_uuid', VARCHAR(40),
                     nullable=False,
                     unique=True),
              Column('os', TEXT),
              Column('platform', TEXT),
              Column('bogomips', DECIMAL),
              Column('system_memory', INT),
              Column('system_swap', INT),
              Column('vendor', TEXT),
              Column('system', TEXT),
              Column('cpu_vendor', TEXT),
              Column('cpu_model', TEXT),
              Column('num_cpus', INT),
              Column('cpu_speed', DECIMAL),
              Column('language', TEXT),
              Column('default_runlevel', INT),
              Column('kernel_version', TEXT),
              Column('formfactor', TEXT),
              Column('last_modified', DATETIME,
                     default=0, nullable=False),
              Column('rating', INT, nullable=False, default=0),
              Column('selinux_enabled', BOOLEAN, nullable=False),
              Column('selinux_policy', TEXT),
              Column('selinux_enforce', TEXT))

myth_systemrole = Column('myth_systemrole', String(32))
mythremote = Column('mythremote', String(32))
myththeme = Column('myththeme', String(32))

def upgrade():
    create_column(myth_systemrole, hosts)
    create_column(mythremote, hosts)
    create_column(myththeme, hosts)


def downgrade():
    drop_column(myth_systemrole, hosts)
    drop_column(mythremote, hosts)
    drop_column(myththeme, hosts)
