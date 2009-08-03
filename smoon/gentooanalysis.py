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

from playmodel import *
from playmodel import _gentoo_distfiles_mirror_rel_table, _gentoo_mirror_pool_table
import datetime
from sqlalchemy.sql import func, select, join


_MAX_DISTFILES_MIRRORS = 20


def _analyze_distfiles_mirrors(session, gentoo_machines):
    def make_row(absolute, label=None):
        res = {
            'absolute':absolute,
            'relative':(absolute * 100.0 / gentoo_machines),
        }
        if label != None:
            res['label'] = label
        return res

    mirror_join = _gentoo_distfiles_mirror_rel_table.join(_gentoo_mirror_pool_table)
    total_mirror_entry_count = session.query(GentooDistfilesMirrorRel).count()
    query = select([GentooMirrorString.name, func.count(GentooDistfilesMirrorRel.machine_id)], \
            from_obj=[mirror_join]).group_by(GentooDistfilesMirrorRel.mirror_id).order_by(\
            func.count(GentooDistfilesMirrorRel.machine_id).desc()).limit(_MAX_DISTFILES_MIRRORS)
    final_rows = []
    others = total_mirror_entry_count
    for i in query.execute().fetchall():
        label, absolute = i
        others = others - absolute
        final_rows.append(make_row(absolute, label))
    if others < 0:
        others = 0

    res = {
        'listed':final_rows,
        'others':[make_row(others)],
        'total':[make_row(total_mirror_entry_count)],
    }
    return res


def gentoo_data_tree(session):
    gentoo_machines = session.query(GentooArchRel).count()
    distfiles_mirrors = _analyze_distfiles_mirrors(session, gentoo_machines)

    # TODO more

    data = {
        'generation_time':datetime.datetime.strftime(\
                datetime.datetime.utcnow(), "%Y-%m-%d %H:%S UTC"),
        'distfiles_mirrors':distfiles_mirrors,
    }
    return data
