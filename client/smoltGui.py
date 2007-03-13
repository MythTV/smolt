#!/usr/bin/python -tt
# Author: Toshio Kuratomi
# License: GPL

import sys
import subprocess
import gtk
from urlparse import urljoin

sys.path.append('/usr/share/smolt/client')

import smolt

smoonURL = 'http://smolt.fedoraproject.org/'

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

        textscroll = gtk.ScrolledWindow()
        textscroll.show()
        layout.pack_start(textscroll, expand=True)

        entry = gtk.TextBuffer()
        entry.set_text(self.profile.getProfile())
        #entry.set_text(self.profile.return_report())
        entryView = gtk.TextView(entry)
        entryView.show()
        textscroll.add(entryView)
        
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
            url = urljoin(smoonURL, '/show?UUID=%s' % self.profile.host.UUID)
            finishMessage = gtk.MessageDialog(self.mainWindow,
                    gtk.DIALOG_DESTROY_WITH_PARENT | gtk.DIALOG_MODAL,
                    gtk.MESSAGE_INFO,
                    gtk.BUTTONS_OK,
                    message_format='The data was successfully sent.  If you need to refer to your hardware profile for a bug report your UUID is \n%s\nstored in /etc/sysconfig/hw-uuid' % self.profile.host.UUID)
        self.mainWindow.hide()
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
