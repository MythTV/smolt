# -*- coding: UTF-8 -*-

# smolt - Fedora hardware profiler
#
# Copyright (C) 2007 Mike McGrath
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
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

'''This file contains various GUI bits that need to be shared between
the firstboot GUI and the normal GUI.'''

import sys
import gtk

sys.path.append('/usr/share/smolt/client')

from i18n import _
import smolt

class HostTable:

    '''This builds a GTK+ table that contains the host data from the
    supplied profile.'''
    
    def __init__(self, profile):
        self.profile = profile
        self.host_table = None
        
    def get(self):
        if self.host_table is None:
            self.host_table = gtk.ScrolledWindow()
            self.host_table.show()

            hostlist = gtk.ListStore(str, str)

            for label, data in self.profile.hostIter():
                hostlist.append([label, data])

            hostview = gtk.TreeView(hostlist)
            hostview.set_property('rules-hint', True)
            hostview.show()
            self.host_table.add(hostview)

            hostlabelcolumn = gtk.TreeViewColumn(_('Label'))
            hostview.append_column(hostlabelcolumn)
            hostlabelcell = gtk.CellRendererText()
            hostlabelcolumn.pack_start(hostlabelcell, True)
            hostlabelcolumn.add_attribute(hostlabelcell, 'text', 0)

            hostdatacolumn = gtk.TreeViewColumn(_('Data'))
            hostview.append_column(hostdatacolumn)
            hostdatacell = gtk.CellRendererText()
            hostdatacolumn.pack_start(hostdatacell, True)
            hostdatacolumn.add_attribute(hostdatacell, 'text', 1)

        return self.host_table

class DeviceTable:
    '''This builds a GTK+ table that contains the device data from the
    supplied profile.'''

    def __init__(self, profile):
        self.profile = profile
        self.device_table = None

    def get(self):
        if self.device_table is None:
            self.device_table = gtk.ScrolledWindow()
            self.device_table.show()

            devicelist = gtk.ListStore(str, str, str, str, str)

            for VendorID, DeviceID, SubsysVendorID, SubsysDeviceID, Bus, Driver, Type, Description in self.profile.deviceIter():
                devicelist.append([5, Bus, Driver, Type, Description])

            deviceview = gtk.TreeView(devicelist)
            deviceview.set_property('rules-hint', True)
            deviceview.show()
            self.device_table.add(deviceview)

#            devicecolumn1 = gtk.TreeViewColumn(_('Rate this device'))
#            deviceview.append_column(devicecolumn1)
#            devicecell1 = StarHScaleCellRender()
#            devicecolumn1.pack_start(devicecell1, True)
#            devicecolumn1.add_attribute(devicecell1, 'value', 0)
#            devicecolumn1.set_sort_column_id(0)

            devicecolumn2 = gtk.TreeViewColumn(_('Bus'))
            deviceview.append_column(devicecolumn2)
            devicecell2 = gtk.CellRendererText()
            devicecolumn2.pack_start(devicecell2, True)
            devicecolumn2.add_attribute(devicecell2, 'text', 1)
            devicecolumn2.set_sort_column_id(1)

            devicecolumn3 = gtk.TreeViewColumn(_('Driver'))
            deviceview.append_column(devicecolumn3)
            devicecell3 = gtk.CellRendererText()
            devicecolumn3.pack_start(devicecell3, True)
            devicecolumn3.add_attribute(devicecell3, 'text', 2)
            devicecolumn3.set_sort_column_id(2)

            devicecolumn4 = gtk.TreeViewColumn(_('Type'))
            deviceview.append_column(devicecolumn4)
            devicecell4 = gtk.CellRendererText()
            devicecolumn4.pack_start(devicecell4, True)
            devicecolumn4.add_attribute(devicecell4, 'text', 3)
            devicecolumn4.set_sort_column_id(3)

            devicecolumn5 = gtk.TreeViewColumn(_('Description'))
            deviceview.append_column(devicecolumn5)
            devicecell5 = gtk.CellRendererText()
            devicecolumn5.pack_start(devicecell5, True)
            devicecolumn5.add_attribute(devicecell5, 'text', 4)
            devicecolumn5.set_sort_column_id(4)

        return self.device_table
