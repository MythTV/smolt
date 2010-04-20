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
parser.add_option('--echo',
                  dest = 'echo',
                  default = False,
                  action = 'store_true',
                  help = 'print SQL queries being run')
parser.add_option('--flush-each',
                  dest = 'flush_each',
                  default = False,
                  action = 'store_true',
                  help = 'flush after each job processed')
parser.add_option('--redo',
                  dest = 'redo',
                  default = False,
                  action = 'store_true',
                  help = 're-process all entries')

(opts, args) = parser.parse_args()

from hardware.featureset import init, config_filename, forward_url, at_final_server, make_client_impl
init(opts.config_file)


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
from hardware.model.model import BatchJob, metadata

warnings.resetwarnings()

# Check if context sensitive things work right
# This script is meant to work with plain SQL alchemy
assert('turbogears' not in sys.modules)


config = ConfigParser()
config.read(config_filename())


CONNECTION = config.get('global', 'sqlalchemy.dburi').\
        lstrip('"\'').rstrip('"\'')
engine = create_engine(CONNECTION, echo=opts.echo)
session = sessionmaker(bind=engine)()

# Check existing tables, create those missing
metadata.create_all(engine)


# TODO
warnings.filterwarnings("ignore")
from hardware.shared.sender import Sender
from urllib2 import HTTPError
warnings.resetwarnings()
if at_final_server():
    sender = None
else:
    sender = Sender(forward_url())
impl = make_client_impl()


def forward(uuid, host):
    assert(not at_final_server())
    print 'FORWARDING to "%s"' % sender.url()
    token = sender.new_token(uuid)
    smolt_protocol = '0.97'

    # Try batch processed version if available
    try:
        response_dict = sender.send('/client/batch_add_json', uuid=uuid, host=host,
            token=token, smolt_protocol=smolt_protocol)
    except HTTPError, e:
        if e.getcode() == 404:
            # Fall back to unbatched version
            response_dict = sender.send('/client/add_json', uuid=uuid, host=host,
                token=token, smolt_protocol=smolt_protocol)
    return response_dict


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
    pub_uuid = None
    try:
        if not at_final_server():
            response_dict = forward(j.hw_uuid, impl.data_for_next_hop(j.data))
            pub_uuid = response_dict['pub_uuid']
        handle_submission(session, j.hw_uuid, pub_uuid, j.data)
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

        if opts.flush_each:
            session.flush()

if not opts.flush_each:
    session.flush()

print '===================================================================='
print '%d jobs processed' % count
print ''
print '% 6d good' % good
print '% 6d bad' % bad
print '----------------------------------'
print '% 6d total' % count
print '===================================================================='
