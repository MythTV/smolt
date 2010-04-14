#!/usr/bin/python
# -*- coding: utf-8 -*-
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

from optparse import OptionParser

# Note: This stuff is up here so we don't get the warnings from inclusions
#   when we don't even use that stuff, e.g. for --help
parser = OptionParser(version = "sss")
parser.add_option('--config',
                  dest = 'config_file',
                  default = None,
                  metavar = 'file.cfg',
                  help = 'override config file to use')
parser.add_option('--delete',
                  dest = 'delete_after_addition',
                  default = False,
                  action = 'store_true',
                  help = 'delete entries after addition (default is marking as added)')
parser.add_option('--redo',
                  dest = 'redo',
                  default = False,
                  action = 'store_true',
                  help = 're-process all entries')

(opts, args) = parser.parse_args()

import warnings
warnings.filterwarnings("ignore")

import sys
import os
import logging
from ConfigParser import ConfigParser
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import traceback

from hardware.submission import handle_submission
from hardware.model.model import BatchJob

warnings.resetwarnings()

# first look on the command line for a desired config file,
# if it's not on the command line, then
# look for setup.py in this directory. If it's not there, this script is
# probably installed
if opts.config_file == None:
    if os.path.exists(os.path.join(os.path.dirname(__file__), "setup.py")):
        opts.config_file = 'dev.cfg'
    else:
        opts.config_file = 'prod.cfg'


config = ConfigParser()
config.read(opts.config_file)
CONNECTION = config.get('global', 'sqlalchemy.dburi').\
        lstrip('"\'').rstrip('"\'')
engine = create_engine(CONNECTION, echo=True)
session = sessionmaker(bind=engine)()

# Check existing tables, create those missing
from sqlalchemy import MetaData
metadata = MetaData()
metadata.create_all(engine)

# Build query base
q = session.query(BatchJob)
if not opts.redo:
    q = q.filter_by(added=False)
q = q.order_by(BatchJob.arrival.asc())

count = q.count()
jobs = q.all()
good = 0
bad = 0
for j in jobs:
    print '===================================================================='
    print 'Processing job with hardware UUID %s' % j.hw_uuid
    print '===================================================================='
    try:
        handle_submission(session, j.hw_uuid, j.data)
        good = good + 1
    except Exception, e:
        (_type, _value, _traceback) = sys.exc_info()
        traceback.print_exception(_type, _value, _traceback)
        bad = bad + 1
    else:
        if opts.delete_after_addition:
            session.delete(j)
        else:
            j.added = True
session.flush()
print '===================================================================='
print '%d jobs processed' % count
print ''
print '% 6d good' % good
print '% 6d bad' % bad
print '----------------------------------'
print '% 6d total' % count
print '===================================================================='
