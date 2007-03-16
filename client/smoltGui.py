#!/usr/bin/python -tt
# -*- coding: UTF-8 -*-
# Author: Toshio Kuratomi

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

import sys
import subprocess
import gtk
from urlparse import urljoin

sys.path.append('/usr/share/smolt/client')

from i18n import _
import smolt

class SmoltGui(object):
    ui = '''<ui>
  <menubar>
    <menu action="File">
      <menuitem action="Send"/>
      <separator/>
      <menuitem action="Quit"/>
    </menu>
    <menu action="Help">
      <menuitem action="Privacy"/>
      <separator/>
      <menuitem action="About"/>
    </menu>
  </menubar>
  <toolbar>
    <toolitem action="Quit"/>
    <separator/>
    <toolitem action="Send"/>
    <separator/>
    <toolitem action="Privacy"/>
  </toolbar>
</ui>
'''
    
    def __init__(self, args):
        self.mainWindow = None
        self.aboutDialog = None
        self.privacyPolicy = None
        
        self.profile = smolt.Hardware()
        self._create_gtk_windows()

    def _create_gtk_windows(self):
        actiongroup = gtk.ActionGroup('actiongroup')
        actiongroup.add_actions([('Quit', gtk.STOCK_QUIT, _('_Quit'), None, _('Quit the program without sending your hardware profile to the server'), self.quit_cb),
                                 ('Send', gtk.STOCK_GO_FORWARD, _('_Send'), '<control>s', _('Send your hardware profile to the server.'), self.send_cb),
                                 ('Privacy', gtk.STOCK_INFO, _('Show _Privacy Policy'), None, _('Show the Smolt privacy policy.'), self.privacy_cb),
                                 ('About', gtk.STOCK_ABOUT, _('_About'), None, None, self.about_cb),
                                 ('File', None, '_File'),
                                 ('Help', None, '_Help')])
        
        uim = gtk.UIManager()
        uim.insert_action_group(actiongroup, 0)
        uim.add_ui_from_string(self.ui)
        accelerators = uim.get_accel_group()
        
        self.mainWindow = gtk.Window()
        self.mainWindow.set_title('Smolt')
        self.mainWindow.connect('delete_event', self.quit_cb)
        self.mainWindow.connect('destroy', self.quit_cb)
        self.mainWindow.add_accel_group(accelerators)
        self.mainWindow.set_default_size(700, 600)
        
        layout = gtk.VBox()
        layout.show()
        self.mainWindow.add(layout)
        
        menubar = uim.get_widget('ui/menubar')
        menubar.show()
        layout.pack_start(menubar, expand=False)
        
        toolbar = uim.get_widget('ui/toolbar')
        toolbar.show()
        layout.pack_start(toolbar, expand=False)
        
        #header = gtk.Label(_('This is the hardware information Smolt will send to the server.'))
        #header.show()
        #layout.pack_start(header, expand=False)

        vpaned = gtk.VPaned()
        vpaned.show()
        layout.pack_start(vpaned, expand = True)
        
        hosttablescroll = gtk.ScrolledWindow()
        hosttablescroll.show()
        vpaned.pack1(hosttablescroll, resize = True, shrink = True)
        
        hostlist = gtk.ListStore(str, str)

        for label, data in self.profile.hostIter():
            hostlist.append([label, data])

        hostview = gtk.TreeView(hostlist)
        hostview.set_property('rules-hint', True)
        hostview.show()
        
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
        
        hosttablescroll.add(hostview)

        devicetablescroll = gtk.ScrolledWindow()
        devicetablescroll.show()
        vpaned.pack2(devicetablescroll, resize = True, shrink = True)
        
        devicelist = gtk.ListStore(str, str, str, str, str)

        for VendorID, DeviceID, SubsysVendorID, SubsysDeviceID, Bus, Driver, Type, Description in self.profile.deviceIter():
            devicelist.append(['%s:%s:%s:%s' % (VendorID, DeviceID, SubsysVendorID, SubsysDeviceID), Bus, Driver, Type, Description])

        deviceview = gtk.TreeView(devicelist)
        deviceview.set_property('rules-hint', True)
        deviceview.show()

        devicecolumn1 = gtk.TreeViewColumn(_('Device ID'))
        deviceview.append_column(devicecolumn1)
        devicecell1 = gtk.CellRendererText()
        devicecolumn1.pack_start(devicecell1, True)
        devicecolumn1.add_attribute(devicecell1, 'text', 0)
        devicecolumn1.set_sort_column_id(0)

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

        devicetablescroll.add(deviceview)

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
                    message_format=_('An error occurred while sending the data to the server.'))
        else:
            url = urljoin(smolt.smoonURL, '/show?UUID=%s' % self.profile.host.UUID)
            finishMessage = gtk.MessageDialog(self.mainWindow,
                    gtk.DIALOG_DESTROY_WITH_PARENT | gtk.DIALOG_MODAL,
                    gtk.MESSAGE_INFO,
                    gtk.BUTTONS_OK,
                    message_format=_('The data was successfully sent.  If you need to refer to your hardware profile for a bug report your UUID is \n%s\nstored in /etc/sysconfig/hw-uuid') % self.profile.host.UUID)
        finishMessage.show()
        finishMessage.run()
        self.quit_cb(None)

    def privacy_cb(self, *extra):
        if self.privacyPolicy is None:
            privacy_text = file('../doc/PrivacyPolicy', 'r').read().strip()
            self.privacyPolicy = gtk.Dialog(_('Smolt Privacy Policy'),
                                            self.mainWindow,
                                            gtk.DIALOG_DESTROY_WITH_PARENT | gtk.DIALOG_MODAL,
                                            (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))
            self.privacyPolicy.connect('response', self.privacy_response_cb)
            self.privacyPolicy.connect('close', self.privacy_close_cb)
            self.privacyPolicy.connect('delete_event', self.privacy_close_cb)
            
            textscroll = gtk.ScrolledWindow()
            textscroll.set_border_width(6)
            textscroll.set_size_request(540, 475)
            textscroll.show()
            self.privacyPolicy.vbox.pack_start(textscroll, expand = True)
            
            textview = gtk.TextView()
            textview.set_editable(False)
            textview.set_cursor_visible(False)
            textview.get_buffer().set_text(privacy_text)
            textview.show()
            textscroll.add(textview)

        self.privacyPolicy.show()

    def privacy_response_cb(self, dialog, response, *args):
        if response < 0:
            dialog.hide()
            dialog.emit_stop_by_name('response')
            
    def privacy_close_cb(self, widget, *args):
        self.aboutDialog.hide()
        return True

    def about_cb(self, *extra):
        if self.aboutDialog is None:
            self.aboutDialog = gtk.AboutDialog()
            self.aboutDialog.set_transient_for(self.mainWindow)
            self.aboutDialog.set_name('Smolt')
            self.aboutDialog.set_version(smolt.smoltProtocol)
            self.aboutDialog.set_website('https://hosted.fedoraproject.org/projects/smolt')
            self.aboutDialog.set_authors(['Mike McGrath <mmcgrath@redhat.com>',
                                          'Jeffrey C. Ollie <jeff@ocjtech.us>',
                                          'Dennis Gilmore <dennis@ausil.us>',
                                          'Toshio Kuratomi <a.badger@gmail.com>'])
            self.aboutDialog.set_comments('Fedora hardware profiler.')
            self.aboutDialog.set_copyright('Copyright © 2007 Mike McGrath')
            self.aboutDialog.set_wrap_license(True)
            self.aboutDialog.set_license('This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.\n\nThis program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.\n\nYou should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.')
            logo = gtk.gdk.pixbuf_new_from_file('smolt-about.png')
            self.aboutDialog.set_logo(logo)
            self.aboutDialog.connect('response', self.about_response_cb)
            self.aboutDialog.connect('close', self.about_close_cb)
            self.aboutDialog.connect('delete_event', self.about_close_cb)
        self.aboutDialog.show()

    def about_response_cb(self, dialog, response, *args):
        if response < 0:
            dialog.hide()
            dialog.emit_stop_by_name('response')
            
    def about_close_cb(self, widget, *args):
        self.aboutDialog.hide()
        return True
        
    def run(self):
        self.mainWindow.show()
        gtk.main()

def url_hook(dialog, link, data):
    print 'url', link

def email_hook(dialog, link, data):
    print 'email', link

if __name__ == '__main__':
    gtk.about_dialog_set_url_hook(url_hook, None)
    gtk.about_dialog_set_email_hook(email_hook, None)
    app = SmoltGui(sys.argv)
    app.run()
    sys.exit(0)

