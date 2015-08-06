# -*- coding: utf-8 -*-
# smolt - Fedora hardware profiler
#
# Copyright (C) 2011 Sebastian Pipping <sebastian@pipping.org>
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

def add_column(query, column):
    """
    Wrapper for SQLAlchemy's deprecated Query.add_column()

    Query.add_columns() was added with SQLAlchemy 0.6.x.
    Query.add_column() is deprecated since 0.6.x.
    """
    if hasattr(query, 'add_columns'):
        return query.add_columns(column)
    else:
        return query.add_column(column)
