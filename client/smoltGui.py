#!/usr/bin/python -tt
# Author: Toshio Kuratomi
# License: GPL

import sys
import subprocess
import gtk
from urlparse import urljoin

sys.path.append('/usr/share/smolt/client')

import smolt

class SmoltGui(object):
    def __init__(self, args):
        self.profile = smolt.Hardware()
        self._create_gtk_windows()

    def _create_gtk_windows(self):
        accelerators = gtk.AccelGroup()
        self.mainWindow = gtk.Window()
        self.mainWindow.connect('delete_event', self.quit_cb)
        self.mainWindow.connect('destroy', self.quit_cb)
        self.mainWindow.add_accel_group(accelerators)
        self.mainWindow.set_default_size(700, 400)

        layout = gtk.VBox()
        layout.show()
        self.mainWindow.add(layout)

        header = gtk.Label('This is the hardware information smolt will send to the server.')
        header.show()
        layout.pack_start(header, expand=False)

        tablescroll = gtk.ScrolledWindow()
        tablescroll.show()
        layout.pack_start(tablescroll, expand=True)
        
        tablevbox = gtk.VBox()
        tablevbox.show()
        tablescroll.add_with_viewport(tablevbox)
        
        hostlist = gtk.ListStore(str, str)

        for label, data in self.profile.hostIter():
            hostlist.append([label, data])

        hostview = gtk.TreeView(hostlist)
        hostview.set_property('rules-hint', True)
        hostview.show()
        
        hostlabelcolumn = gtk.TreeViewColumn('Label')
        hostview.append_column(hostlabelcolumn)
        hostlabelcell = gtk.CellRendererText()
        hostlabelcolumn.pack_start(hostlabelcell, True)
        hostlabelcolumn.add_attribute(hostlabelcell, 'text', 0)

        hostdatacolumn = gtk.TreeViewColumn('Data')
        hostview.append_column(hostdatacolumn)
        hostdatacell = gtk.CellRendererText()
        hostdatacolumn.pack_start(hostdatacell, True)
        hostdatacolumn.add_attribute(hostdatacell, 'text', 1)
        
        tablevbox.pack_start(hostview, expand=True)

        devicelist = gtk.ListStore(str, str, str, str, str)

        for VendorID, DeviceID, SubsysVendorID, SubsysDeviceID, Bus, Driver, Type, Description in self.profile.deviceIter():
            devicelist.append(['%s:%s:%s:%s' % (VendorID, DeviceID, SubsysVendorID, SubsysDeviceID), Bus, Driver, Type, Description])

        deviceview = gtk.TreeView(devicelist)
        deviceview.set_property('rules-hint', True)
        deviceview.show()

        devicecolumn1 = gtk.TreeViewColumn('Device ID')
        deviceview.append_column(devicecolumn1)
        devicecell1 = gtk.CellRendererText()
        devicecolumn1.pack_start(devicecell1, True)
        devicecolumn1.add_attribute(devicecell1, 'text', 0)
        devicecolumn1.set_sort_column_id(0)

        devicecolumn2 = gtk.TreeViewColumn('Bus')
        deviceview.append_column(devicecolumn2)
        devicecell2 = gtk.CellRendererText()
        devicecolumn2.pack_start(devicecell2, True)
        devicecolumn2.add_attribute(devicecell2, 'text', 1)
        devicecolumn2.set_sort_column_id(1)

        devicecolumn3 = gtk.TreeViewColumn('Driver')
        deviceview.append_column(devicecolumn3)
        devicecell3 = gtk.CellRendererText()
        devicecolumn3.pack_start(devicecell3, True)
        devicecolumn3.add_attribute(devicecell3, 'text', 2)
        devicecolumn3.set_sort_column_id(2)

        devicecolumn4 = gtk.TreeViewColumn('Type')
        deviceview.append_column(devicecolumn4)
        devicecell4 = gtk.CellRendererText()
        devicecolumn4.pack_start(devicecell4, True)
        devicecolumn4.add_attribute(devicecell4, 'text', 3)
        devicecolumn4.set_sort_column_id(3)

        devicecolumn5 = gtk.TreeViewColumn('Description')
        deviceview.append_column(devicecolumn5)
        devicecell5 = gtk.CellRendererText()
        devicecolumn5.pack_start(devicecell5, True)
        devicecolumn5.add_attribute(devicecell5, 'text', 4)
        devicecolumn5.set_sort_column_id(4)

        tablevbox.pack_start(deviceview, expand=True)

        buttonbox = gtk.HBox()
        buttonbox.show()
        layout.pack_start(buttonbox, expand=False)

        closeButton = gtk.Button('_Cancel')
        closeButton.show()
        buttonbox.add(closeButton)
        closeButton.connect('clicked', self.quit_cb)
        closeButton.add_accelerator('clicked', accelerators,
                ord('W'), gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)
        
        sendButton = gtk.Button('_Send')
        sendButton.show()
        buttonbox.add(sendButton)
        sendButton.connect('clicked', self.send_cb)

    def quit_cb(self, *extra):
        '''Quit the program.'''
        gtk.main_quit()

    def send_cb(self, *extra):
        '''Send the profile to the smolt server'''
        # A little hacky.  Perhaps this should be a method in the library
        #retcode = subprocess.call('/usr/bin/smoltSendProfile -a')
        retcode = self.profile.send()
        if retcode:
            finishMessage = gtk.MessageDialog(self.mainWindow,
                    gtk.DIALOG_DESTROY_WITH_PARENT | gtk.DIALOG_MODAL,
                    gtk.MESSAGE_WARNING,
                    gtk.BUTTONS_OK,
                    message_format='An error occurred while sending the data to the server.')
        else:
            url = urljoin(smolt.smoonURL, '/show?UUID=%s' % self.profile.host.UUID)
            finishMessage = gtk.MessageDialog(self.mainWindow,
                    gtk.DIALOG_DESTROY_WITH_PARENT | gtk.DIALOG_MODAL,
                    gtk.MESSAGE_INFO,
                    gtk.BUTTONS_OK,
                    message_format='The data was successfully sent.  If you need to refer to your hardware profile for a bug report your UUID is \n%s\nstored in /etc/sysconfig/hw-uuid' % self.profile.host.UUID)
        finishMessage.show()
        finishMessage.run()
        self.quit_cb(None)

    def run(self):
        self.mainWindow.show()
        gtk.main()

if __name__ == '__main__':
    app = SmoltGui(sys.argv)
    app.run()
    sys.exit(0)
