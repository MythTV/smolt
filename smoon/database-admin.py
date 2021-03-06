# -*- coding: utf-8 -*-
# smolt - Fedora hardware profiler
#
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
PROG = 'smoonDatabaseAdmin'
USAGE = 'Usage: %prog [options] (create|drop)+'
VERSION = '%prog 1.0'
parser = OptionParser(prog=PROG, usage=USAGE, version=VERSION)
parser.add_option('--config',
                  dest = 'config_file',
                  default = None,
                  metavar = 'file.cfg',
                  help = 'override config file to use')
parser.add_option('--force',
                  dest = 'force',
                  default = False,
                  action = 'store_true',
                  help = 'apply more force')
parser.add_option('--fake-mysql',
                  dest = 'fake_mysql',
                  default = False,
                  action = 'store_true',
                  help = 'operate on fake MySQL database instance and print SQL')
parser.add_option('--echo',
                  dest = 'echo',
                  default = False,
                  action = 'store_true',
                  help = 'echo SQL statements')
(opts, args) = parser.parse_args()


# Import sits down here to reduce load time
import sys
if not args:
    parser.print_help()
    sys.exit(1)

# Import sits down here to reduce load time
# .. and to save import warnings if we don't get here
import os
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from ConfigParser import ConfigParser

from hardware.featureset import init, config_filename, this_is, GENTOO, MYTH_TV
init(opts.config_file)

# Import without warnings on stderr
stderr_backup = sys.stderr
class DevNull:
    def write(self, data):
        pass
    def flush(self):
        pass
sys.stderr = DevNull()
from hardware.model.model import metadata
if this_is(GENTOO):
    from hardware.model.model_gentoo import *

if this_is(MYTH_TV):
    from hardware.model.model_mythtv import *

sys.stderr = stderr_backup

config = ConfigParser()
config.read(config_filename())
CONNECTION = config.get('global', 'sqlalchemy.dburi').\
        lstrip('"\'').rstrip('"\'')


if opts.fake_mysql:
    from StringIO import StringIO
    buf = StringIO()
    def statement_dumper(s, p=''):
        for i in (s, p):
            if i:
                buf.write(i.strip() + '\n\n')
    engine = create_engine('mysql://', strategy='mock', executor=statement_dumper)
else:
    engine = create_engine(CONNECTION, echo=opts.echo)

session = sessionmaker(bind=engine)()

for command in args:
    if command == 'drop':
        if not opts.fake_mysql and not opts.force:
            sys.stderr.write('Skipping command "drop", option "--force" required\n')
        else:
            sys.stderr.write('Dropping all model-related tables\n')
            metadata.drop_all(engine)
    elif command == 'create':
        sys.stderr.write('Creating model-related tables%s\n' % (opts.force and ' (without prior check for existence)' or ''))
        try:
            metadata.create_all(engine, checkfirst=(not opts.force))
        except sqlalchemy.exc.OperationalError, e:
            print 'FAILED, error is', str(e)

if opts.fake_mysql:
    sys.stdout.write(buf.getvalue())
