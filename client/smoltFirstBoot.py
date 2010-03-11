from gtk import *
import string
import gtk
import gobject
import sys
import os
import commands

from firstboot.config import *
from firstboot.constants import *
from firstboot.functions import *
from firstboot.module import *

try:
    import subprocess
except ImportError, e:
    pass


# Based off of the EULA

##
## I18N
## 
import gettext
import locale
try:
    locale.setlocale(locale.LC_ALL, '')
except locale.Error:
    locale.setlocale(locale.LC_ALL, 'C')
if os.path.isdir('po'):
    t = gettext.translation('smolt', 'po', fallback = True)
else:
    t = gettext.translation('smolt', '/usr/share/locale', fallback = True)

_ = t.gettext

class moduleClass(Module):
    def __init__(self):
        Module.__init__(self)
        self.priority = 107
        self.sidebarTitle = _("Hardware Profile")
        self.title = _("Hardware Profile")
        self.icon = "smolt.png"

    def apply(self, interface, testing=False):
        if self.ok_button.get_active() == True:
            if testing:
                import logging
                logging.info("Running in testing mode, so not sending information")
                return RESULT_SUCCESS

            # You'd think I know better than this.
            # So would I.
            try: 
                result = subprocess.call(['/sbin/chkconfig', 'smolt', 'on'])
                result = subprocess.Popen(['/usr/bin/smoltSendProfile', '-r', '-a'])
            except NameError:
                result = os.system(' '.join(['/sbin/chkconfig', 'smolt', 'on']))
                result = os.system(' '.join(['/usr/bin/smoltSendProfile', '-r', '-a']))
            return RESULT_SUCCESS
        else:
            dlg = gtk.MessageDialog(None, 0, gtk.MESSAGE_QUESTION, gtk.BUTTONS_NONE,
                (_("Are you sure you wouldn't like to send the profile?  " 
                "Submitting your profile is a valuable source of information "
                "for our development and can help troubleshoot issues that "
                "may come up with your hardware.")))

            dlg.set_position(gtk.WIN_POS_CENTER)
            dlg.set_modal(True)

            continue_button = dlg.add_button(_("_Reconsider sending"), 0)
            shutdown_button = dlg.add_button(_("_No, do not send."), 1)
            continue_button.grab_focus()

            rc = dlg.run()
            dlg.destroy()

            if rc == 0:
                return RESULT_FAILURE
            elif rc == 1:
                return RESULT_SUCCESS

    def createScreen(self):
        self.vbox = gtk.VBox()
        self.vbox.set_size_request(400, 200)

        internal_vbox = gtk.VBox()
        internal_vbox.set_border_width(10)
        internal_vbox.set_spacing(5)

        text_buffer = gtk.TextBuffer()
        text_view = gtk.TextView()
        text_view.set_editable(False)
        text_sw = gtk.ScrolledWindow()
        text_sw.set_shadow_type(gtk.SHADOW_IN)
        text_sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        text_sw.add(text_view)

        label = gtk.Label(_("Smolt is a hardware profiler for The Fedora "
                "Project.  Submitting your profile is a great way to give back "
                "to the community as this information is used to help focus our"
                " efforts on popular hardware and platforms.  Submissions are "
                "anonymous.  Sending your profile will enable a monthly "
                "check-in."))

        label.set_line_wrap(True)
        label.set_alignment(0.0, 0.5)
        label.set_size_request(500, -1)
        internal_vbox.pack_start(label, False, True)


        iter = text_buffer.get_iter_at_offset(0)
        # Generate the UUID if it does not exist yet
        if not os.path.exists('/etc/smolt/hw-uuid'):
            s=open('/proc/sys/kernel/random/uuid', 'r')
            d=open('/etc/smolt/hw-uuid','w')
            d.write(s.read())
            s.close()
            d.close()
            
        for line in subprocess.Popen(['/usr/bin/smoltSendProfile', '-p'],
            stdout=subprocess.PIPE).stdout:
            text_buffer.insert(iter, line)

        text_view.set_buffer(text_buffer)
        
        self.kernel_oops = gtk.CheckButton(_("_Participate in KernelOOPS"))
        self.bodhi = gtk.CheckButton(_("Submit profile link to _Bodhi"))

        self.ok_button = gtk.RadioButton(None, (_("_Send Profile")))
        self.no_button = gtk.RadioButton(self.ok_button, (_("D_o not send profile")))
        self.no_button.set_active(True)

        internal_vbox.pack_start(text_sw, True)
#        internal_vbox.pack_start(self.kernel_oops, False)
#        internal_vbox.pack_start(self.bodhi, False)
        internal_vbox.pack_start(self.ok_button, False)
        internal_vbox.pack_start(self.no_button, False)

        self.vbox.pack_start(internal_vbox, True, 5)

    def initializeUI(self):
        pass
