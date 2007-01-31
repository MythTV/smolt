from gtk import *
import string
import gtk
import gobject
import sys
import functions
import rhpl.iconv
import os
import commands

# Based off of the EULA

##
## I18N
## 
import gettext
gettext.bindtextdomain ("firstboot", "/usr/share/locale")
gettext.textdomain ("firstboot")
_=gettext.gettext

class childWindow:
    #You must specify a runPriority for the order in which you wish your module to run
    runPriority = 107
    moduleName = (_("Smolt"))

    def launch(self, doDebug = None):
        self.doDebug = doDebug
        if self.doDebug:
            print "initializing smolt module"

        self.vbox = gtk.VBox()
        self.vbox.set_size_request(400, 200)

        msg = (_("Smolt"))

        title_pix = functions.imageFromFile("workstation.png")

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

        iter = textBuffer.get_iter_at_offset(0)

        for line in os.popen('/usr/bin/smoltPrint', 'r'):
        textBuffer.insert(iter, line)

        textView.set_buffer(textBuffer)
            
        self.okButton = gtk.RadioButton(None, (_("_Yes, I'd like to send my hardware profile")))
        self.noButton = gtk.RadioButton(self.okButton, (_("N_o, I do not want to send my hardware profile")))
        self.noButton.set_active(True)

        internalVBox.pack_start(textSW, True)
        internalVBox.pack_start(self.okButton, False)
        internalVBox.pack_start(self.noButton, False)
        
        self.vbox.pack_start(internalVBox, True, 5)
        return self.vbox, title_pix, msg

    def apply(self, notebook):
        if self.okButton.get_active() == True:
        result = commands.getstatusoutput('/usr/bin/smoltSendProfile')
            return 0
        else:
            dlg = gtk.MessageDialog(None, 0, gtk.MESSAGE_QUESTION, gtk.BUTTONS_NONE,
                                    (_("Are you sure you wouldn't like to send the profile?  " 
                                       "Submitting your profile is a valuable source of information "
                                       "for our development and can help troubleshoot issues that "
                                       "may come up with your hardware ")))

            dlg.set_position(gtk.WIN_POS_CENTER)
            dlg.set_modal(True)

            continueButton = dlg.add_button(_("_Reconsider sending"), 0)
            shutdownButton = dlg.add_button(_("_No, do not send."), 1)
            continueButton.grab_focus()

            rc = dlg.run()
            dlg.destroy()

            if rc == 0:
                return None
            elif rc == 1:
                return 0

