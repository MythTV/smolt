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
from playmodel import _gentoo_accept_keyword_rel_table, _gentoo_keyword_pool_table
import datetime
from sqlalchemy.sql import func, select, join, and_


_MAX_DISTFILES_MIRRORS = 20


class GentooReporter:
    def __init__(self, session):
        self.session = session
        self.gentoo_machines = 1
        self._data = {}

    def _relative(self, absolute):
        return round(absolute * 100.0 / self.gentoo_machines, 1)

    def _analyze_archs(self):
        # TODO use different type of join?
        def make_row(absolute_stable, absolute_unstable, absolute_total, label=None):
            res = {
                'absolute_stable':absolute_stable,
                'absolute_unstable':absolute_unstable,
                'absolute_total':absolute_total,
                'relative_stable':self._relative(absolute_stable),
                'relative_unstable':self._relative(absolute_unstable),
                'relative_total':self._relative(absolute_total),
            }
            if label != None:
                res['label'] = label
            return res

        columns = [GentooKeywordString.name, func.count(GentooAcceptKeywordRel.machine_id), func.sum(GentooAcceptKeywordRel.stable)]
        pool_join = _gentoo_accept_keyword_rel_table.join(_gentoo_keyword_pool_table)
        arch_join_condition = and_(GentooArchRel.keyword_id == GentooAcceptKeywordRel.keyword_id,\
                GentooArchRel.machine_id == GentooAcceptKeywordRel.machine_id)
        query = select(columns, from_obj=[pool_join]).where(arch_join_condition).\
                group_by(GentooArchRel.keyword_id).order_by(\
                func.count(GentooAcceptKeywordRel.machine_id).desc())
        total_stable = 0
        total_unstable = 0
        total_total = 0
        final_rows = []
        for i in query.execute().fetchall():
            label, total, stable = i
            stable = long(stable)
            unstable = total - stable
            if unstable < 0:
                unstable = 0

            total_stable = total_stable + stable
            total_unstable = total_unstable + unstable
            total_total = total_total + total

            final_rows.append(make_row(total_stable, total_unstable, total_total, label))

        res = {
            'listed':final_rows,
            'total':[make_row(total_stable, total_unstable, total_total)],
        }
        return res

    def _analyze_distfiles_mirrors(self):
        def make_row(absolute, label=None):
            res = {
                'absolute':absolute,
                'relative':self._relative(absolute),
            }
            if label != None:
                res['label'] = label
            return res

        mirror_join = _gentoo_distfiles_mirror_rel_table.join(_gentoo_mirror_pool_table)
        total_mirror_entry_count = self.session.query(GentooDistfilesMirrorRel).count()
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

    # TODO testing
    def _explain_time_delta(self, d):
        def numerus(number):
            if number == 1:
                return ''
            else:
                return 's'

        def format_seconds(s):
            return '%d second%s' % (seconds, numerus(seconds))

        words = []
        if d.days > 0:
            words.append('%d day%s' % (d.days, numerus(d.days)))
        seconds = d.seconds
        hours = seconds / 3600
        seconds = seconds - 3600 * hours
        minutes = seconds / 60
        seconds = seconds - 60 * minutes
        if hours > 0:
            words.append('%d hour%s' % (hours, numerus(hours)))
        if minutes > 0:
            words.append('%d minute%s' % (minutes, numerus(minutes)))

        if words:
            words.append(format_seconds(seconds))
            return ', '.join(words[:-1]) + ' and ' + words[-1]
        else:
            if seconds == 0:
                return 'less than 1 second'
            else:
                return format_seconds(seconds)

    def gather(self):
        report_begun = datetime.datetime.utcnow()
        self.gentoo_machines = self.session.query(GentooArchRel).count()
        distfiles_mirrors = self._analyze_distfiles_mirrors()
        archs = self._analyze_archs()
        report_finished = datetime.datetime.utcnow()
        generation_duration = self._explain_time_delta(\
                report_finished - report_begun)
        data = {
            'generation_time':datetime.datetime.strftime(\
                    report_finished, "%Y-%m-%d %H:%S UTC"),
            'generation_duration':generation_duration,
            'distfiles_mirrors':distfiles_mirrors,
            'archs':archs,
        }
        self._data = data

    def data(self):
        return self._data


def gentoo_data_tree(session):
    gentoo_reporter = GentooReporter(session)
    gentoo_reporter.gather()
    return gentoo_reporter.data()
