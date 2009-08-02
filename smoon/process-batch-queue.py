#!/usr/bin/python
# smolt - Fedora hardware profiler
#
# Copyright (C) 2007 Mike McGrath
# Copyright (C) 2009 Sebastian Pipping <sebastian@pipping.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301, USA.

import sys
import os
import logging
from ConfigParser import ConfigParser
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from hardware.submission import handle_submission
from hardware.model.model import BatchJob


# first look on the command line for a desired config file,
# if it's not on the command line, then
# look for setup.py in this directory. If it's not there, this script is
# probably installed
if len(sys.argv) > 1:
    configfile = sys.argv[1]
elif os.path.exists(os.path.join(os.path.dirname(__file__), "setup.py")):
    configfile = 'dev.cfg'
else:
    configfile = 'prod.cfg'


config = ConfigParser()
config.read(configfile)
CONNECTION = config.get('global', 'sqlalchemy.dburi').\
        lstrip('"\'').rstrip('"\'')
engine = create_engine(CONNECTION, echo=True)
session = sessionmaker(bind=engine)()

count = session.query(BatchJob).order_by(BatchJob.arrival).count()
jobs = session.query(BatchJob).order_by(BatchJob.arrival).all()
for j in jobs:
    print '===================================================================='
    print 'Processing job with hardware UUID %s' % j.hw_uuid
    print '===================================================================='
    try:
        handle_submission(session, j.hw_uuid, j.data)
    except Exception, e:
        logging.debug('Caught exception: %s' % e.message)
    session.delete(j)
session.flush()
print '===================================================================='
print '%d jobs processed' % count
print '===================================================================='
