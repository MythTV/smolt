# If your project uses a database, you can set up database tests
# similar to what you see below. Be sure to set the db_uri to
# an appropriate uri for your testing database. sqlite is a good
# choice for testing, because you can use an in-memory database
# which is very fast.

import turbogears
from turbogears import testutil, database
from hardware.model import *
from hardware import model

turbogears.update_config(configfile='../test.cfg', modulename='hardware.config')


#def test_add():
#
#    host = Host.query().selectone_by(uuid="fish")
#    print host.uuid
#
#    assert host.uuid != 'fish'
#    host.delete()
#    host.flush()

