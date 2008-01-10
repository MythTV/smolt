from gtk import *
import string
import gtk
import gobject
import sys
import rhpl.iconv
import os
import commands

from firstboot.config import *
from firstboot.constants import *
from firstboot.functions import *
from firstboot.module import *

# Based off of the EULA

##
## I18N
## 
import gettext
import locale
locale.setlocale(locale.LC_ALL, '')
if os.path.isdir('po'):
    t = gettext.translation('smolt', 'po', fallback = True)
else:
    t = gettext.translation('smolt', '/usr/share/locale', fallback = True)
#gettext.bindtextdomain ("smolt", "/usr/share/locale")
#gettext.textdomain ("smolt")
#_=gettext.gettext

_ = t.gettext

class moduleClass(Module):
    def __init__(self):
        Module.__init__(self)
        self.priority = 107
        self.sidebarTitle = _("Hardware Profile")
        self.title = _("Hardware Profile")
        self.icon = "smolt.png"

    def apply(self, interface, testing=False):
        if self.okButton.get_active() == True:
            if testing:
                import logging
                logging.info("Running in testing mode, so not sending information")
                return RESULT_SUCCESS

            # You'd think I know better than this.
            result = os.system('/sbin/chkconfig smolt on')
            result = os.system('/usr/bin/smoltSendProfile -r -a &')
            return RESULT_SUCCESS
        else:
            dlg = gtk.MessageDialog(None, 0, gtk.MESSAGE_QUESTION, gtk.BUTTONS_NONE,
                (_("Are you sure you wouldn't like to send the profile?  " 
                "Submitting your profile is a valuable source of information "
                "for our development and can help troubleshoot issues that "
                "may come up with your hardware.")))

            dlg.set_position(gtk.WIN_POS_CENTER)
            dlg.set_modal(True)

            continueButton = dlg.add_button(_("_Reconsider sending"), 0)
            shutdownButton = dlg.add_button(_("_No, do not send."), 1)
            continueButton.grab_focus()

            rc = dlg.run()
            dlg.destroy()

            if rc == 0:
                return RESULT_FAILURE
            elif rc == 1:
                return RESULT_SUCCESS

    def createScreen(self):
        self.vbox = gtk.VBox()
        self.vbox.set_size_request(400, 200)

        internalVBox = gtk.VBox()
        internalVBox.set_border_width(10)
        internalVBox.set_spacing(5)

        textBuffer = gtk.TextBuffer()
        textView = gtk.TextView()
        textView.set_editable(False)
        textSW = gtk.ScrolledWindow()
        textSW.set_shadow_type(gtk.SHADOW_IN)
        textSW.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        textSW.add(textView)

        label = gtk.Label(_("Smolt is a hardware profiler for The Fedora "
                "Project.  Submitting your profile is a great way to give back "
                "to the community as this information is used to help focus our"
                " efforts on popular hardware and platforms.  Submissions are "
                "anonymous.  Sending your profile will enable a monthly update."))

        label.set_line_wrap(True)
        label.set_alignment(0.0, 0.5)
        label.set_size_request(500, -1)
        internalVBox.pack_start(label, False, True)


        iter = textBuffer.get_iter_at_offset(0)

        for line in os.popen('/usr/bin/smoltSendProfile -p', 'r'):
        	textBuffer.insert(iter, line)

        textView.set_buffer(textBuffer)

        self.okButton = gtk.RadioButton(None, (_("_Send Profile")))
        self.noButton = gtk.RadioButton(self.okButton, (_("D_o not send profile")))
        self.noButton.set_active(True)

        internalVBox.pack_start(textSW, True)
        internalVBox.pack_start(self.okButton, False)
        internalVBox.pack_start(self.noButton, False)

        self.vbox.pack_start(internalVBox, True, 5)

    def initializeUI(self):
        pass
