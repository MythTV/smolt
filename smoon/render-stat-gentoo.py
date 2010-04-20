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

import turbogears
from turbogears.view import engines
from turbogears import update_config
from turbogears.database import session

from hardware.featureset import init, config_filename
from reportutils import _process_output


import sys
_cfg_filename = None
if len(sys.argv) > 1:
    _cfg_filename = sys.argv[1]

init(_cfg_filename)
update_config(configfile=config_filename(),modulename="hardware.config")


turbogears.view.load_engines()
engine = engines.get('genshi', None)

page_path = "hardware/static/stats"


def do_distro_specific_rendering():
    import gentooanalysis
    import datetime
    gentoo_data_tree = gentooanalysis.gentoo_data_tree(session)
    t = engine.load_template('hardware.templates.gentoo')
    out_html = _process_output(engine, dict(data=gentoo_data_tree), template=t, format='html')
    fname = "%s/gentoo.html" % (page_path)
    f = open(fname, "w")
    f.write(out_html)
    f.close()

    t = engine.load_template('hardware.templates.gentoo_zero_installs_packages')
    out_txt = _process_output(engine, dict(data=gentoo_data_tree), template=t, format='html')
    # Kill HTML intro and outro. TODO Resolve dirty hack
    out_txt = '\n'.join(e for e in out_txt.split('\n') if not e.startswith('<'))
    fname = "%s/gentoo_zero_installs_packages.txt" % (page_path)
    f = open(fname, "w")
    f.write(out_txt)
    f.close()

do_distro_specific_rendering()
