#
# TUI for RHN Registration
# Copyright (c) 2000-2002 Red Hat, Inc.
#
# Author:
#       Adrian Likins <alikins@redhat.com>
#       Preston Brown <pbrown@redhat.com>

from os import geteuid
import sys
import string

from rhpl.translate import _

import snack

import signal

import rhnreg, hardware
import up2dateErrors
import up2dateUtils
import rpmUtils
import rpcServer
import up2dateLog
import config
import up2dateAuth
from rhn import rpclib

from rhnreg_constants import *

log = up2dateLog.initLog()
cfg = config.initUp2dateConfig()

def FatalErrorWindow(screen, errmsg):
    snack.ButtonChoiceWindow(screen, FATAL_ERROR, "%s" % errmsg,
                             [OK])
    screen.finish()
    sys.exit(1)
    
def RecoverableErrorWindow(screen, errmsg):
    snack.ButtonChoiceWindow(screen, RECOVERABLE_ERROR, "%s" % errmsg,
                             [OK])

def WarningWindow(screen, errmsg):
    snack.ButtonChoiceWindow(screen, WARNING, "%s" % errmsg,
                             [OK])
    screen.finish()
    
def ConfirmQuitWindow(screen):
    button = snack.ButtonChoiceWindow(screen, CONFIRM_QUIT,
                             CONFIRM_QUIT_TXT,
                             [CONTINUE_REGISTERING, REGISTER_LATER2],
                             width = 70)

    if button == string.lower(REGISTER_LATER2):
        screen.finish()
        return 1
    else:
        return 0
    
    
def tui_call_wrapper(screen, func, *params):

    try:
        results = func(*params)
    except up2dateErrors.CommunicationError, e:
        FatalErrorWindow(screen, HOSTED_CONNECTION_ERROR % cfg['serverURL'])
    except up2dateErrors.SSLCertificateVerifyFailedError, e:
        FatalErrorWindow(screen, e.errmsg)
    except up2dateErrors.AuthenticationOrAccountCreationError, e:
        RecoverableErrorWindow(screen, e.errmsg)
        return 0
    except up2dateErrors.NoBaseChannelError, e:
        FatalErrorWindow(screen, e.errmsg + '\n' + 
                         BASECHANNELERROR % (up2dateUtils.getArch(), 
                                             up2dateUtils.getOSRelease(),
                                             up2dateUtils.getVersion()))
    except up2dateErrors.SSLCertificateFileNotFound, e:
        FatalErrorWindow(screen, e.errmsg + '\n\n' +
                         SSL_CERT_FILE_NOT_FOUND_ERRER)
        
    return results

class ConnectWindow:

    def __init__(self, screen, tui):
        self.name = "ConnectWindow"
        self.screen = screen
        self.tui = tui
        size = snack._snack.size()

        self.server = self.tui.serverURL

        fixed_server_url = rhnreg.makeNiceServerUrl(self.server)

        #Save the config only if the url is different
        if fixed_server_url != self.server:
            self.server = fixed_server_url
            cfg.set('serverURL', self.server)

            cfg.save()
        
        self.proxy = cfg['httpProxy']

        toplevel = snack.GridForm(self.screen, CONNECT_WINDOW, 1, 1)

        text = CONNECT_WINDOW_TEXT % self.server + "\n\n"

        if self.proxy:
            text += CONNECT_WINDOW_TEXT2 % self.proxy

        tb = snack.Textbox(size[0]-30, size[1]-20, 
                           text,
                           1, 1)

        toplevel.add(tb, 0, 0, padding = (0, 0, 0, 1))                           

        self.g = toplevel


    def run(self):
        log.log_debug("Running %s" % self.__class__.__name__)

        # We draw and display the window.  The window gets displayed as
        # long as we are attempting to connect to the server.  Once we
        # connect the window is gone.
        result = self.g.draw()
        self.screen.refresh()
        tui_call_wrapper(self.screen, rhnreg.getCaps)
            
        self.screen.popWindow()

        # Next, test for RHEL 5 compatibility.
        if rhnreg.serverSupportsRhelFiveCalls():
            pass
        else:
            FatalErrorWindow(self.screen, 
                             _("The server you are attempting "
                               "to register against does not support this "
                               "version of the client."))

        # Just return next, although the user wouldn't have actually pressed
        # anything.
        return "next"

    def saveResults(self):
        pass
    
class StartWindow:
    
    def __init__(self, screen, tui):
        self.name = "StartWindow"
        self.screen = screen
        self.tui = tui
        size = snack._snack.size()
        toplevel = snack.GridForm(self.screen, START_REGISTER_WINDOW,
                                  1, 2)

        start_register_text = START_REGISTER_TEXT
        if self.tui.serverType == 'hosted':
            start_register_text += START_REGISTER_TEXT_H

        tb = snack.Textbox(size[0]-10, size[1]-14, start_register_text, 1, 1)
        toplevel.add(tb, 0, 0, padding = (0, 0, 0, 1))

        self.bb = snack.ButtonBar(self.screen,
                                  [(WHY_REGISTER, "why_register"),
                                   (NEXT, "next"),
                                   (CANCEL, "cancel")])
        toplevel.add(self.bb, 0, 1, growx = 1)

        self.g = toplevel

    def saveResults(self):
        pass


    def run(self):
        log.log_debug("Running %s" % self.__class__.__name__)
        result = self.g.runOnce()
        button = self.bb.buttonPressed(result)

        if result == "F12":
            return "next"
        elif button == "why_register":
            why_reg_win = WhyRegisterWindow(self.screen, self.tui)
            why_reg_win.run()
            return button

        return button

class WhyRegisterWindow:

    def __init__(self, screen, tui):
        self.name = "WhyRegisterWindow"
        self.screen = screen
        self.tui = tui
        size = snack._snack.size()
        toplevel = snack.GridForm(self.screen, WHY_REGISTER_WINDOW,
                                  1, 2)


        why_register_text = WHY_REGISTER_TEXT + "\n\n" + \
                            WHY_REGISTER_SEC  + "\n" + \
                            WHY_REGISTER_SEC_TXT + "\n\n" + \
                            WHY_REGISTER_DLD + "\n" + \
                            WHY_REGISTER_DLD_TXT + "\n\n" + \
                            WHY_REGISTER_SUPP + "\n" + \
                            WHY_REGISTER_SUPP_TXT + "\n\n" + \
                            WHY_REGISTER_COMP + "\n" + \
                            WHY_REGISTER_COMP_TXT + "\n\n" + \
                            WHY_REGISTER_TIP

        tb = snack.Textbox(size[0]-10, size[1]-14, why_register_text, 1, 1)

        toplevel.add(tb, 0, 0, padding = (0, 0, 0, 1))


        self.bb = snack.ButtonBar(self.screen,
                                  [(BACK_REGISTER, "back")])
        toplevel.add(self.bb, 0, 1, growx = 1)

        self.g = toplevel

        self.screen.gridWrappedWindow(toplevel, 'WhyRegisterWindow', 80, 24)

    def run(self):
        log.log_debug("Running %s" % self.__class__.__name__)
        result = self.g.runOnce()
        button = self.bb.buttonPressed(result)

        return button
    

class PrivacyWindow:

    def __init__(self, screen, tui):
        self.name = "PrivacyWindow"
        self.screen = screen
        self.tui = tui
        size = snack._snack.size()
        toplevel = snack.GridForm(screen, PRIVACY_WINDOW,
                                  1, 2)

        try:
            tb = snack.Textbox(size[0]-10, size[1]-14, rhnreg.privacyText(), 1)
        except up2dateErrors.CommunicationError, e:
            FatalErrorWindow(screen, e.errmsg)

        toplevel.add(tb, 0, 0, padding = (0, 0, 0, 1))

        self.bb = snack.ButtonBar(screen,
                                  [(NEXT, "next"),
                                   (BACK, "back"),
                                   (CANCEL, "cancel")])
        toplevel.add(self.bb, 0, 1, growx = 1)
        self.g = toplevel


    def saveResults(self):
        pass

    def run(self):
        log.log_debug("Running %s" % self.__class__.__name__)
        self.screen.refresh()
        result = self.g.runOnce()
        button = self.bb.buttonPressed(result)

        if result == "F12":
            return "next"
        return button

class TermsAndConditionsWindow:
    def __init__(self, screen, tui):
        self.name = "TermsAndConditionsWindow"
        self.screen = screen
        self.tui = tui
        size = snack._snack.size()
        toplevel = snack.GridForm(screen, TERMS_AND_CONDS_WINDOW,
                                  1, 2)

        try:
            text = """ \n\n\n This is a sample Terms and Conditions. \n\n\n"""
            print "#FIXME"
            # text  = rhnreg.termsAndConditions()
            tb = snack.Textbox(size[0]-10, size[1]-14, text, 1)
        except up2dateErrors.CommunicationError, e:
            FatalErrorWindow(screen, e.errmsg)

        toplevel.add(tb, 0, 0, padding = (0, 0, 0, 1))

        self.bb = snack.ButtonBar(screen,
                                  [(NEXT, "next"),
                                   (BACK, "back"),
                                   (CANCEL, "cancel")])
        toplevel.add(self.bb, 0, 1, growx = 1)
        self.g = toplevel
        
    def saveResults(self):
        pass

    def run(self):
        log.log_debug("Running %s" % self.__class__.__name__)
        self.screen.refresh()
        result = self.g.runOnce()
        button = self.bb.buttonPressed(result)

        if result == "F12":
            return "next"
        return button
    
class InfoWindow:

    def __init__(self, screen, tui):
        self.name = "InfoWindow"
        self.screen = screen
        self.tui = tui
        self.tui.alreadyRegistered = 0

        self.server = self.tui.serverURL
        
        size = snack._snack.size()

        toplevel = snack.GridForm(screen, REGISTER_WINDOW, 1, 12)
 
        # Satellite
        if self.tui.serverType == 'satellite':
            label = snack.Textbox(size[0]-10, 3,
                                  LOGIN_PROMPT % self.server, 
                                  scroll = 0, wrap = 1)
            toplevel.add(label, 0, 0, anchorLeft = 1)

            grid = snack.Grid(2, 3)

            label = snack.Label(LOGIN) 
            grid.setField(label, 0, 0, padding = (0, 0, 1, 0),
                          anchorRight = 1)

            self.userNameEntry = snack.Entry(20)
            self.userNameEntry.set(tui.userName)
            grid.setField(self.userNameEntry, 1, 0, anchorLeft = 1)

            label = snack.Label(PASSWORD)
            grid.setField(label, 0, 1, padding = (0, 0, 1, 0),
                          anchorRight = 1)

            try:
                self.passwordEntry = snack.Entry(20, password = 1)
            except TypeError:
                self.passwordEntry = snack.Entry(20, hidden = 1)
            self.passwordEntry.set(tui.password)
            grid.setField(self.passwordEntry, 1, 1, anchorLeft = 1)

            toplevel.add(grid, 0, 3)

            label = snack.TextboxReflowed(size[0]-10, LOGIN_TIP)
            toplevel.add(label, 0, 4, anchorLeft=1)

            # BUTTON BAR
            self.bb = snack.ButtonBar(screen,
                                      [(NEXT, "next"),
                                       (BACK, "back"),
                                       (CANCEL, "cancel")])

        # Hosted
        else:
            label = snack.TextboxReflowed(size[0]-10,HOSTED_LOGIN_PROMPT)
            toplevel.add(label, 0, 0, anchorLeft = 1)

            grid = snack.Grid(2, 3)

            label = snack.Label(HOSTED_LOGIN)
            grid.setField(label, 0, 0, padding = (0, 0, 1, 0),
                          anchorRight = 1)

            self.userNameEntry = snack.Entry(20)
            self.userNameEntry.set(tui.userName)
            grid.setField(self.userNameEntry, 1, 0, anchorLeft = 1)

            label = snack.Label(PASSWORD)
            grid.setField(label, 0, 1, padding = (0, 0, 1, 0),
                          anchorRight = 1)

            try:
                self.passwordEntry = snack.Entry(20, password = 1)
            except TypeError:
                self.passwordEntry = snack.Entry(20, hidden = 1)
            self.passwordEntry.set(tui.password)
            grid.setField(self.passwordEntry, 1, 1, anchorLeft = 1)

            toplevel.add(grid, 0, 3)


            # BUTTON BAR
            self.bb = snack.ButtonBar(screen,
                                      [(NEW_LOGIN, "new_login"),
                                       (NEXT, "next"),
                                       (BACK, "back"),
                                       (CANCEL, "cancel")])

        toplevel.add(self.bb, 0, 8, padding = (0, 1, 0, 0),
                 growx = 1)


        self.g = toplevel


    def validateFields(self):
        if self.userNameEntry.value() == "":
            snack.ButtonChoiceWindow(self.screen, ERROR,
                                     USER_REQUIRED,
                                     buttons = [OK])
            self.g.setCurrent(self.userNameEntry)
            return 0
        if self.passwordEntry.value() == "":
            snack.ButtonChoiceWindow(self.screen, ERROR,
                                     PASSWORD_REQUIRED,
                                     buttons = [OK])
            self.g.setCurrent(self.passwordEntry)
            return 0


        return 1


    def saveResults(self):
        if self.tui.userName == '':
            self.tui.userName = self.userNameEntry.value()
        if self.tui.password == '':
            self.tui.password = self.passwordEntry.value()

       
        
    def run(self):
        log.log_debug("Running %s" % self.__class__.__name__)
        self.screen.refresh()
        valid = 0
        while not valid:
            result = self.g.run()
            button = self.bb.buttonPressed(result)

            if result == "F12":
                button = "next"

            if button == "new_login":
                pw = ProductWindow(self.screen, self.tui)
                pw_results = pw.run()

                if pw_results == "next":
                    pw.saveResults()

                self.screen.popWindow()
                return pw_results

            if button == "next":

                valid = self.validateFields()
                if valid == 0:
                    continue
                
                # Now that we have username, look up the groups for that user
                # if we're going against hosted.
                if self.tui.serverType == 'hosted':
                    orgs = rhnreg.PossibleOrgs()
                    orgs = tui_call_wrapper(self.screen, 
                                            rhnreg.getPossibleOrgs, 
                                            self.userNameEntry.value(),
                                            self.passwordEntry.value())

                    if orgs == None or orgs == 0:
                        valid = 0
                        continue
                    
                    self.tui.orgs = orgs.getOrgs()
                    self.tui.default_org = orgs.getDefaultOrg()

                    if len(self.tui.orgs) > 1:
                        self.tui.hasMultipleOrgs = 1
                        
                    self.tui.other['org_id'] = self.tui.default_org

            else:
                break

        self.screen.popWindow()
        return button
    
class OrgGroupWindow:

    def __init__(self, screen, tui):
        self.name = "OrgGroupWindow"
        self.screen = screen
        self.tui = tui
        self.size = snack._snack.size()
        

        toplevel = snack.GridForm(screen, ORG_SELECT, 1, 4)
        tb = snack.Textbox(self.size[0]-10, self.size[1]-15, 
                           ORG_SELECT_PROMPT % self.tui.userName + "\n\n",
                           wrap = 1)
                           
        toplevel.add(tb, 0, 0, anchorLeft = 1)    
        
        label = snack.Label(ORG_PROMPT)
        toplevel.add(label, 0, 1, anchorLeft = 1)    
        
        buttonlist = []
        
        if self.tui.orgs != None:
            for org_group_id, org_group_label in self.tui.orgs.items():
                if org_group_id == self.tui.default_org:
                    buttonlist.append((org_group_label, org_group_id, 1))
                else:
                    buttonlist.append((org_group_label, org_group_id, 0))

        self.org_group_select_list = snack.RadioBar(self.screen, buttonlist)
        toplevel.add(self.org_group_select_list, 0, 2)
    
        self.g = toplevel
        
        # BUTTON BAR
        self.bb = snack.ButtonBar(screen,
                                  [(NEXT, "next"),
                                   (BACK, "back"),
                                   (CANCEL, "cancel")])
        toplevel.add(self.bb, 0, 3, padding = (0, 1, 0, 0),
                     growx = 1)        
        
    def run(self):
        log.log_debug("Running %s" % self.__class__.__name__)
        self.tui.saw_org_window = 1
        self.screen.refresh()
        valid = 0
        while not valid:
            result = self.g.run()
            button = self.bb.buttonPressed(result)

            if result == "F12":
                button = "next"

            if button == "next":
                valid = self.validateFields()
            else:
                break

            if button == "next":
                valid = self.validateFields()
            else:
                break

        self.screen.popWindow()
        return button        
        
    def validateFields(self):
        if self.org_group_select_list.getSelection() != None:
            return 1
        else:
            return 0


    def saveResults(self):
        self.tui.other['org_id'] = self.org_group_select_list.getSelection()
        log.log_debug('Set org_id as %s' % self.tui.other['org_id'])
        return 1

    
class SubscriptionWindow:

    def __init__(self, screen, tui):
        self.name = "SubscriptionWindow"
        self.screen = screen
        self.tui = tui
        self.size = snack._snack.size()
    
        toplevel = snack.GridForm(screen, SUBSCRIPTION_WINDOW, 1, 18)

        grid = snack.Grid(1, 1)
        text = snack.Textbox(self.size[0]-10, 3, SUBSCRIPTION_INTRO, wrap = 1)
        grid.setField(text, 0, 0, anchorLeft = 1)

        toplevel.add(grid, 0, 0)

        grid = snack.Grid(1,1)
        subscription_text = SUBSCRIPTION_INFO + "\n\n" + \
                            "* " + SUBSCRIPTION_CHOICE1 + "\n\n" + \
                             "* " + SUBSCRIPTION_CHOICE2 + "\n\n"

        # Determine which text to show based on if we've already activated a
        # number.
        if self.tui.activated_now == 1:
            subscription_text += "* " + SUBSCRIPTION_CHOICE3_ALT + "\n"
        else:
            subscription_text += "* " + SUBSCRIPTION_CHOICE3 + "\n"

        textbox = snack.Textbox(self.size[0]-10, self.size[1]-17,
                                text = subscription_text,
                                wrap = 1,
                                scroll = 1)

        grid.setField(textbox, 0, 0)
        toplevel.add(grid, 0, 1)

        grid=snack.Grid(1,1)
        text = snack.Textbox(1, 1, '')
        grid.setField(text, 0, 0)
        toplevel.add(grid, 0, 2)

        grid = snack.Grid(2, 2)

        label = snack.Label(ENTITLEMENT_NUM_PROMPT)
        grid.setField(label, 0, 0)
        self.entNumEntry = snack.Entry(40)
        
        if self.tui.other['registration_number'] == None:
            self.entNumEntry.set('')
        else:
            self.entNumEntry.set(self.tui.other['registration_number'])
            
        grid.setField(self.entNumEntry, 1, 0, padding = (1, 0, 0, 0),
                      anchorLeft = 1)
        label = snack.Label(' ')
        grid.setField(label, 0, 1)
        label = snack.Label(ENTITLEMENT_NUM_EXAMPLE)
        grid.setField(label, 1, 1, anchorLeft = 1)

        toplevel.add(grid, 0, 3)

        self.g = toplevel

        # BUTTON BAR
        self.bb = snack.ButtonBar(screen,
                                  [(NEXT, "next"),
                                   (BACK, "back"),
                                   (CANCEL, "cancel")])
        toplevel.add(self.bb, 0, 4, padding = (0, 1, 0, 0),
                     growx = 1)


    def run(self):
        log.log_debug("Running %s" % self.__class__.__name__)
        self.screen.refresh()
        self.tui.saw_sub_window = 1
        valid = 0
        while not valid:
            result = self.g.run()
            button = self.bb.buttonPressed(result)

            if result == "F12":
                button = "next"

            if button == "next":
                valid = self.validateFields()
            else:
                break

        self.screen.popWindow()
        return button        
        
    def validateFields(self):
        
        if self.entNumEntry.value() != '':
            
            # Now, activate the entitlement number
            # Send up org_id if we've got one.
            try:
                if self.tui.other.has_key('org_id'):
                    self.tui.activate_result = \
                                rhnreg.activateRegistrationNumber(
                                             self.tui.userName, 
                                             self.tui.password, 
                                             self.entNumEntry.value(),
                                             self.tui.other['org_id'])
                else:
                    self.tui.activate_result = \
                                rhnreg.activateRegistrationNumber(
                                             self.tui.userName, 
                                             self.tui.password, 
                                             self.entNumEntry.value())

                if self.tui.activate_result.getStatus() == \
                   rhnreg.ActivationResult.ACTIVATED_NOW:
                    return 1                                         
                else:
                     RecoverableErrorWindow(self.screen, ALREADY_USED_NUMBER)
                     return 0

            except up2dateErrors.InvalidRegistrationNumberError:
                RecoverableErrorWindow(self.screen, INVALID_NUMBER %
                                       self.entNumEntry.value())
                return 0
            except up2dateErrors.NotEntitlingError:
                RecoverableErrorWindow(self.screen, NONENTITLING_NUMBER)
                return 0
        else:
             snack.ButtonChoiceWindow(self.screen, ERROR,
                         _("You must enter an Installation Number that " +
                           "activates subscriptions in your account."),
                         buttons = [OK])
             return 0


    def saveResults(self):
        self.tui.other['registration_number'] = self.entNumEntry.value()
        rhnreg.writeRegNum(self.entNumEntry.value())

class ProductWindow:

    def __init__(self, screen, tui):
        self.name = "ProductWindow"
        self.screen = screen
        self.tui = tui

        toplevel = snack.GridForm(screen, PRODUCT_WINDOW, 1, 18)
                    
        grid = snack.Grid(1, 2)
        tb = snack.TextboxReflowed(70, PRODUCT_WINDOW_PROMPT)
        grid.setField(tb, 0, 0, anchorLeft = 1)

        label = snack.Label(" ")
        grid.setField(label, 0, 1)

        toplevel.add(grid, 0, 0) 
        
        grid = snack.Grid(4, 5)

        label = snack.Label(_("Login Information:"))
        grid.setField(label, 0, 0, anchorLeft = 1)

        label = snack.Label(HOSTED_LOGIN_ENTRY)
        grid.setField(label, 0, 1, anchorLeft = 1)
        self.hostedLoginEntry = snack.Entry(16)
        grid.setField(self.hostedLoginEntry, 1, 1, padding = (1, 0, 0, 0),
                      anchorLeft = 1)

        # label = snack.Label(HOSTED_LOGIN_ENTRY_TIP)
        # grid.setField(label, 1, 2, anchorLeft = 1)

        label = snack.Label(" ")
        # grid.setField(label, 0, 2)
        # grid.setField(label, 0, 3)

        label = snack.Label(HOSTED_PASSWORD_ENTRY)
        grid.setField(label, 0, 4, anchorLeft = 1)
        try:
            self.passwordEntry = snack.Entry(16, password=1)
        except TypeError:
            self.passwordEntry = snack.Entry(16, hidden=1)
        grid.setField(self.passwordEntry, 1, 4, padding = (1, 0, 0, 0),
                      anchorLeft = 1)

        label = snack.Label(PASSWORD_VERIFY)
        grid.setField(label, 2, 4, anchorRight = 1)
        try:
            self.passwordVerifyEntry = snack.Entry(16, password=1)
        except TypeError:
            self.passwordVerifyEntry = snack.Entry(16, hidden=1)
        grid.setField(self.passwordVerifyEntry, 3, 4, padding = (1, 0, 0, 0),
                      anchorLeft = 1)

        toplevel.add(grid, 0, 1, anchorLeft = 1)

        grid = snack.Grid(1, 1)
        label = snack.Label("")
        grid.setField(label, 0, 0, anchorLeft = 1)
        
        toplevel.add(grid, 0, 2, anchorLeft = 1)

        grid = snack.Grid(1, 1)
    
        label = snack.Label(_("Account Information:"))
        grid.setField(label, 0, 0, anchorLeft = 1)
        toplevel.add(grid, 0, 3, anchorLeft = 1)

        grid = snack.Grid(4, 3)

        label = snack.Label(_("*First Name:"))
        grid.setField(label, 0, 0, anchorLeft = 1)
        self.firstNameEntry = snack.Entry(20)
        self.firstNameEntry.set(tui.productInfo['first_name'])
        grid.setField(self.firstNameEntry, 1, 0, padding = (1, 0, 0, 0),
                      anchorLeft = 1)

        label = snack.Label(_("*Last Name:"))
        grid.setField(label, 2, 0, padding = (1, 0, 0, 0), anchorRight = 1)
        self.lastNameEntry = snack.Entry(25)
        self.lastNameEntry.set(tui.productInfo['last_name'])
        grid.setField(self.lastNameEntry, 3, 0, padding = (1, 0, 0, 0),
                      anchorLeft = 1)

        label = snack.Label(EMAIL)
        grid.setField(label, 0, 1, anchorLeft = 1)
        self.emailAddressEntry = snack.Entry(20)
        grid.setField(self.emailAddressEntry, 1, 1, padding = (1, 0, 0, 0),
                      anchorLeft = 1)

        label = snack.Label(_("*Company Name:"))
        grid.setField(label, 0, 2, anchorLeft = 1)
        self.companyEntry = snack.Entry(20)
        self.companyEntry.set(tui.productInfo['company'])
        grid.setField(self.companyEntry, 1, 2, padding = (1, 0, 0, 0),
                      anchorLeft = 1)

        toplevel.add(grid, 0, 4, anchorLeft = 1)

        grid = snack.Grid(1, 2)
        label = snack.Label(COMPANY_TIP)
        grid.setField(label, 0, 0, anchorLeft = 1)

        label = snack.Label(" ")
        grid.setField(label, 0, 1)

        toplevel.add(grid, 0, 5, anchorLeft  = 1)

        grid = snack.Grid(4, 4)

        label = snack.Label(_("Street Address:"))
        grid.setField(label, 0, 0, anchorLeft = 1)
        self.address1Entry = snack.Entry(20)
        self.address1Entry.set(tui.productInfo['address'])
        grid.setField(self.address1Entry, 1, 0, padding = (1, 0, 0, 0),
                      anchorLeft = 1)

        label = snack.Label(_("City:"))
        grid.setField(label, 0, 1, anchorLeft = 1)
        self.cityEntry = snack.Entry(20)
        self.cityEntry.set(tui.productInfo['city'])
        grid.setField(self.cityEntry, 1, 1, padding = (1, 0, 0, 0),
                      anchorLeft = 1)

        label = snack.Label(_("State/Province:"))
        grid.setField(label, 2, 1, padding = (1, 0, 0, 0), anchorRight = 1)
        self.stateEntry = snack.Entry(20)
        self.stateEntry.set(tui.productInfo['state'])
        grid.setField(self.stateEntry, 3, 1, padding = (1, 0, 0, 0),
                      anchorLeft = 1)

        label = snack.Label(_("Zip/Post Code:"))
        grid.setField(label, 0, 2, anchorLeft = 1)
        self.zipEntry = snack.Entry(7)
        self.zipEntry.set(tui.productInfo['zip'])
        grid.setField(self.zipEntry, 1, 2, padding = (1, 0, 0, 0),
                      anchorLeft = 1)
 
        label = snack.Label(_("*Country:"))
        grid.setField(label, 2, 2, padding = (1, 0, 0, 0), anchorLeft = 1)
        self.countryEntry = snack.Entry(20)
        self.countryEntry.set(tui.productInfo['country'])
        grid.setField(self.countryEntry, 3, 2, padding = (1, 0, 0, 0),
                      anchorLeft = 1)

        toplevel.add(grid, 0, 6, anchorLeft = 1)


        grid = snack.Grid(1, 1)
        label = snack.Label("")
        grid.setField(label, 0, 0, anchorLeft = 1)
        
        toplevel.add(grid, 0, 7, anchorLeft = 1)


        # BUTTON BAR
        self.bb = snack.ButtonBar(screen,
                                  [(NEXT, "next"),
                                   (BACK, "back"),
                                   (CANCEL, "cancel")])
        toplevel.add(self.bb, 0, 9, padding = (0, 1, 0, 0),
                     growx = 1)

        self.g = toplevel


    def validateFields(self):

        if self.hostedLoginEntry.value() == "":
            snack.ButtonChoiceWindow(self.screen, ERROR,
                                     USER_REQUIRED,
                                     buttons = [OK])
            self.g.setCurrent(self.hostedLoginEntry)
            return 0
        if self.passwordEntry.value() == "" or \
           self.passwordVerifyEntry.value() == "":
            snack.ButtonChoiceWindow(self.screen, ERROR,
                                     PASSWORD_REQUIRED,
                                     buttons = [OK])
            self.g.setCurrent(self.passwordEntry)
            return 0
        if self.passwordEntry.value() != self.passwordVerifyEntry.value():
            snack.ButtonChoiceWindow(self.screen, ERROR,
                                     PASSWORD_MISMATCH,
                                     buttons = [OK])
            self.g.setCurrent(self.passwordVerifyEntry)
            return 0
        if self.firstNameEntry.value() == "":
            snack.ButtonChoiceWindow(self.screen, ERROR,
                                     FIRST_NAME_REQD,
                                     buttons = [OK])
            self.g.setCurrent(self.firstNameEntry)
            return 0
        if self.lastNameEntry.value() == "":
            snack.ButtonChoiceWindow(self.screen, ERROR,
                                     LAST_NAME_REQD,
                                     buttons = [OK])
            self.g.setCurrent(self.lastNameEntry)
            return 0
        if self.countryEntry.value() == "":
            snack.ButtonChoiceWindow(self.screen, ERROR,
                                     COUNTRY_REQD,
                                     buttons = [OK])
            self.g.setCurrent(self.countryEntry)
            return 0
        if self.emailAddressEntry.value() == "":
            snack.ButtonChoiceWindow(self.screen, ERROR,
                                     EMAIL_ADDR_REQD,
                                      buttons = [OK])
            self.g.setCurrent(self.emailAddressEntry)
            return 0

        if not rhnreg.validateEmail(self.emailAddressEntry.value()):
            snack.ButtonChoiceWindow(self.screen, ERROR,
                                      EMAIL_ADDR_VERIFY,
                                      buttons = [OK])
            self.g.setCurrent(self.emailAddressEntry)
            return 0
           

        try:
            results = tui_call_wrapper(self.screen, rhnreg.reserveUser, 
                             self.hostedLoginEntry.value(),
                             self.passwordEntry.value())
            # We successfully reserved the user, so return 1 indicating all is
            # well.
            return 1
        except up2dateErrors.ValidationError, e:
            snack.ButtonChoiceWindow(self.screen, ERROR,
                                     _("The server indicated an error:\n") + \
                                     e.errmsg,
                                     buttons = [OK])
            self.g.setCurrent(self.hostedLoginEntry)
            return 0
        except up2dateErrors.LoginMinLengthError, e:
            snack.ButtonChoiceWindow(self.screen, ERROR,
                                     LOGIN_TOO_SHORT + "\n\n" + \
                                     e.errmsg,
                                     buttons = [OK])
            self.g.setCurrent(self.hostedLoginEntry)
            return 0
        except up2dateErrors.PasswordMinLengthError, e:
            snack.ButtonChoiceWindow(self.screen, ERROR,
                                     PASSWORD_TOO_SHORT + "\n\n" + \
                                     e.errmsg,
                                     buttons = [OK])
            self.g.setCurrent(self.passwordEntry)
            return 0
        except up2dateErrors.PasswordMaxLengthError, e:
            snack.ButtonChoiceWindow(self.screen, ERROR,
                                     PASSWORD_TOO_LONG + "\n\n" + \
                                     e.errmsg,
                                     buttons = [OK])
            self.g.setCurrent(self.passwordEntry)
            return 0
            

        return 1


    def saveResults(self):
        self.tui.productInfo['first_name'] = self.firstNameEntry.value()
        self.tui.productInfo['last_name'] = self.lastNameEntry.value()
        self.tui.productInfo['company'] = self.companyEntry.value() or "none"
        self.tui.productInfo['address'] = self.address1Entry.value()
        self.tui.productInfo['city'] = self.cityEntry.value()
        self.tui.productInfo['state'] = self.stateEntry.value()
        self.tui.productInfo['zip'] = self.zipEntry.value()
        self.tui.productInfo['country'] = self.countryEntry.value()
        self.tui.userName = self.hostedLoginEntry.value()
        self.tui.password = self.passwordEntry.value()
        self.tui.email = self.emailAddressEntry.value()

        # Go ahead and create the user.
        # The user has to be created by the time we get to the Hardware
        # window.
        try:
            tui_call_wrapper(self.screen, rhnreg.registerUser,
                             self.tui.userName, self.tui.password,
                             self.tui.email)
        except up2dateErrors.ValidationError, e:
            snack.ButtonChoiceWindow(self.screen, ERROR,
                                     _("The server indicated an error:\n") + \
                                     e.errmsg,
                                     buttons = [OK])
            self.g.setCurrent(self.hostedLoginEntry)
            return 0


    
    def run(self):
        log.log_debug("Running %s" % self.__class__.__name__)
        valid = 0
        while not valid:
            result = self.g.run()
            button = self.bb.buttonPressed(result)

            if result == "F12":
                button = "next"

            if button == "next":
                valid = self.validateFields()
            else:
                break

        self.screen.popWindow()
        return button


class HardwareWindow:

    def __init__(self, screen, tui):
        self.name = "HardwareWindow"
        self.screen = screen
        self.tui = tui
        size = snack._snack.size()

        # read all hardware in
        tui.hardware = hardware.Hardware()
        
        toplevel = snack.GridForm(screen, _("Register a System Profile - Hardware"),
                                  1, 8)

        text = snack.TextboxReflowed(70, _("A Profile Name is a descriptive name that you choose to identify this System Profile on the Red Hat Network web pages. Optionally, include a computer serial or identification number."))

        toplevel.add(text, 0, 0, anchorLeft = 1)

        grid = snack.Grid(2, 2)

        label = snack.Label(_("Profile name:"))
        grid.setField(label, 0, 0, padding = (0, 0, 1, 0), anchorRight = 1)

        self.profileEntry = snack.Entry(40)
        grid.setField(self.profileEntry, 1, 0, anchorLeft = 1)

        toplevel.add(grid, 0, 1, anchorLeft = 1)
        
        if tui.includeHardware:
            self.hardwareButton = snack.Checkbox(_("Include the following information about hardware and network:"), isOn = 1)
        else:
            self.hardwareButton = snack.Checkbox(_("Include the following information about hardware and network:"))
            
        toplevel.add(self.hardwareButton, 0, 2, padding = (0, 1, 0, 0),
                     anchorLeft = 1)

        label = snack.Label(DESELECT)
        toplevel.add(label, 0, 3, anchorLeft = 1, padding = (0, 0, 0, 1))

        grid = snack.Grid(4, 3)
        hardware_text = ''

        hardware_text += _("Version: ") + up2dateUtils.getVersion() + "  "
        self.versionLabel = snack.Label(_("Version: "))
        grid.setField(self.versionLabel, 0, 0, padding = (0, 0, 1, 0), anchorLeft = 1)

        self.versionLabel2 = snack.Label(up2dateUtils.getVersion())
        grid.setField(self.versionLabel2, 1, 0, anchorLeft = 1)

        hardware_text += _("CPU model: ")

        for hw in tui.hardware:            
            if hw['class'] == 'CPU':
                hardware_text += hw['model'] +"\n"
                
        hardware_text += _("Hostname: ")

        for hw in tui.hardware:
            if hw['class'] == 'NETINFO':
                hardware_text += hw['hostname'] + "\n"

                if tui.profileName != "":
                    self.profileEntry.set(tui.profileName)
                else:
                    self.profileEntry.set(hw['hostname'])

        hardware_text += _("CPU speed: ")

        for hw in tui.hardware:            
            if hw['class'] == 'CPU':
                hardware_text += _("%d MHz") % hw['speed'] + "  "

        hardware_text += _("IP Address: ")

        for hw in tui.hardware:
            if hw['class'] == 'NETINFO':
                hardware_text += hw['ipaddr'] + "  "

        hardware_text += _("Memory: ")

        for hw in tui.hardware:
            if hw['class'] == 'MEMORY':
                hardware_text += _("%s megabytes") % hw['ram']

        tb = snack.TextboxReflowed(80, hardware_text)
        toplevel.add(tb, 0, 4)

        self.additionalHWLabel = snack.TextboxReflowed(size[0]-10, _("Additional hardware information including PCI devices, disk sizes and mount points will be included in the profile."))

        toplevel.add(self.additionalHWLabel, 0, 5, padding = (0, 1, 0, 0),
                     anchorLeft = 1)
        
        # BUTTON BAR
        self.bb = snack.ButtonBar(screen,
                                  [(NEXT, "next"),
                                   (BACK, "back"),
                                   (CANCEL, "cancel")])
        toplevel.add(self.bb, 0, 6, padding = (0, 1, 0, 0),
                     growx = 1)

        self.g = toplevel

        # self.screen.gridWrappedWindow(toplevel, 'HardwareWindow', 80, 14)

    def saveResults(self):
        self.tui.profileName = self.profileEntry.value()
        self.tui.includeHardware = self.hardwareButton.selected()

    def run(self):
        log.log_debug("Running %s" % self.__class__.__name__)
        result = self.g.runOnce()
        button = self.bb.buttonPressed(result)

        if result == "F12":
            return "next"
        return button

class PackagesWindow:

    def __init__(self, screen, tui):
        self.name = "PackagesWindow"
        self.screen = screen
        self.tui = tui
        size = snack._snack.size()
        toplevel = snack.GridForm(screen, _("Register a System Profile - Packages"),
                                  1, 7)
        self.g = toplevel


        text = snack.TextboxReflowed(size[0]-10, _("RPM information is important to determine what updated software packages are relevant to this system."))

        toplevel.add(text, 0, 1, anchorLeft = 1)

        self.packagesButton = snack.Checkbox(_("Include RPM packages installed on this system in my System Profile"), 1)
        toplevel.add(self.packagesButton, 0, 2, padding = (0, 1, 0, 1),
                     anchorLeft = 1)

        label = snack.Label(_("You may deselect individual packages by unchecking them below."))
        toplevel.add(label, 0, 3, anchorLeft = 1)

        #self.packageList = snack.Listbox(size[1]-18, 1, width = size[0]-10)
        self.packageList = snack.CheckboxTree(size[1]-18, 1)
        toplevel.add(self.packageList, 0, 4)

        # do we need to read the packages from disk?
        if tui.packageList == []:
            self.pwin = snack.GridForm(screen, _("Building Package List"),
                               1, 1)

            self.scale = snack.Scale(40, 100)
            self.pwin.add(self.scale, 0, 0)
            self.pwin.draw()
            self.screen.refresh()
            getInfo = 0
            if rhnreg.cfg['supportsExtendedPackageProfile']:
                getInfo = 1
            tui.packageList = rpmUtils.getInstalledPackageList(getInfo=getInfo)
            tui.packageList.sort(cmp = lambda x,y: cmp(x.lower(), y.lower()),
                key = lambda x: x[0])
            self.screen.popWindow()

        for package in tui.packageList:
            self.packageList.append("%s-%s-%s" % (package[0],
                                                  package[1],
                                                  package[2]),
                                                  item = package[0],
                                                  selected = 1)
            
        # BUTTON BAR
        self.bb = snack.ButtonBar(screen,
                                  [(NEXT, "next"),
                                   (BACK, "back"),
                                   (CANCEL, "cancel")])
        toplevel.add(self.bb, 0, 5, padding = (0, 1, 0, 0),
                     growx = 1)



    def setScale(self, amount, total):
        self.scale.set(int(((amount * 1.0)/ total) * 100))
        self.pwin.draw()
        self.screen.refresh()
        

    def saveResults(self):
        self.tui.includePackages = self.packagesButton.selected()
        selection = self.packageList.getSelection()
        for pkg in self.tui.packageList:
            if pkg[0] in selection:
                self.tui.selectedPackages.append(pkg)

        
    def run(self):
        log.log_debug("Running %s" % self.__class__.__name__)
        result = self.g.runOnce()
        button = self.bb.buttonPressed(result)

        if result == "F12":
            return "next"
        return button

class SendWindow:

    def __init__(self, screen, tui):
        self.screen = screen
        self.tui = tui
        self.name = "SendWindow"
        size = snack._snack.size()
        
        toplevel = snack.GridForm(screen, _("Send Profile Information to Red Hat Network"),
                                  1, 2)

        text = snack.TextboxReflowed(size[0]-15, SEND_WINDOW)
        toplevel.add(text, 0, 0)

        # BUTTON BAR
        self.bb = snack.ButtonBar(screen,
                                  [(NEXT, "next"),
                                   (BACK, "back"),
                                   (CANCEL, "cancel")])
        toplevel.add(self.bb, 0, 1, padding = (0, 1, 0, 0),
                     growx = 1)

        self.g = toplevel

    def saveResults(self):
        pass


    def run(self):
        log.log_debug("Running %s" % self.__class__.__name__)
        result = self.g.runOnce()
        button = self.bb.buttonPressed(result)

        if result == "F12":
            return "next"
        return button

class FinishWindow:

    def __init__(self, screen, tui):
        self.name = "FinishWindow"
        self.screen = screen
        self.tui = tui
        size = snack._snack.size()
        
        toplevel = snack.GridForm(screen, FINISH_WINDOW,
                                  1, 2)

        text = snack.TextboxReflowed(size[0]-11, FINISH_WINDOW_TEXT_TUI)
        toplevel.add(text, 0, 0)
        
        # BUTTON BAR
        self.bb = snack.ButtonBar(screen,
                                  [(_("Finish"), "next")])
        toplevel.add(self.bb, 0, 1, padding = (0, 1, 0, 0),
                     growx = 1)

        self.g = toplevel

        self.pwin = snack.GridForm(screen, _("Sending Profile to Red Hat Network"),
                                   1, 1)

        self.scale = snack.Scale(40, 100)
        self.pwin.add(self.scale, 0, 0)
        self.pwin.draw()
        self.screen.refresh()

        # send the data
        try:
            rhnreg.registerUser(tui.userName, tui.password, tui.email)
        except up2dateErrors.CommunicationError, e:
            FatalErrorWindow(self.screen, _("Problem registering login name:\n") + e.errmsg)
        except:
            log.log_exception(*sys.exc_info())
            FatalErrorWindow(self.screen, _("Problem registering login name."))

        self.setScale(1, 5)


        reg_info = None
        try:
            # reg_info dict contains: 'system_id', 'channels', 
            # 'failed_channels', 'slots', 'failed_slots'
            reg_info = rhnreg.registerSystem2(tui.userName, tui.password,
                                             tui.profileName, 
                                             other = self.tui.other)
            reg_info = reg_info.rawDict

            systemId = reg_info['system_id']
        except up2dateErrors.CommunicationError, e:
            FatalErrorWindow(self.screen, 
                             _("Problem registering system:\n") + e.errmsg)
        except up2dateErrors.RhnUuidUniquenessError, e:
            FatalErrorWindow(self.screen, 
                             _("Problem registering system:\n") + e.errmsg)
        except up2dateErrors.ActivationKeyUsageLimitError, e:
            FatalErrorWindow(self.screen,
                             ACT_KEY_USAGE_LIMIT_ERROR)
        except:
            log.log_exception(*sys.exc_info())
            FatalErrorWindow(self.screen, _("Problem registering system."))

        # write the system id out.
        if not rhnreg.writeSystemId(systemId):
            FatalErrorWindow(self.screen, 
                             _("Problem writing out system id to disk."))

        self.setScale(2, 5)

        # include the info from the oeminfo file as well
        self.oemInfo = rhnreg.getOemInfo()
        
        # dont send if already registered, do send if they have oemInfo
        if ( not self.tui.alreadyRegistered ) or ( len(self.oemInfo)):
            # send product registration information
            if rhnreg.cfg['supportsUpdateContactInfo']:
                try:
                    rhnreg.updateContactInfo(tui.userName, tui.password,  self.tui.productInfo)
                except up2dateErrors.CommunicationError, e:
                    FatalErrorWindow(self.screen, _("Problem registering personal information:\n") + e.errmsg)
                except:
                    print sys.exc_info()
                    print sys.exc_type
                    
                    FatalErrorWindow(self.screen, 
                                     _("Problem registering personal information"))
                    
            else:
                rhnreg.registerProduct(systemId, self.tui.productInfo,self.tui.oemInfo)
                try:
                    rhnreg.registerProduct(systemId, self.tui.productInfo,self.tui.oemInfo)
                except up2dateErrors.CommunicationError, e:
                    FatalErrorWindow(self.screen, 
                                     _("Problem registering personal information:\n") + 
                                     e.errmsg)
                except:
                    log.log_exception(*sys.exc_info())
                    FatalErrorWindow(self.screen, _("Problem registering personal information"))

        self.setScale(3, 5)

        # maybe upload hardware profile
        if tui.includeHardware:
            try:
                rhnreg.sendHardware(systemId, tui.hardware)
            except up2dateErrors.CommunicationError, e:
                FatalErrorWindow(self.screen,
                                 _("Problem sending hardware profile:\n") + e.errmsg)
            except:
                log.log_exception(*sys.exc_info())
                FatalErrorWindow(self.screen,
                                 _("Problem sending hardware profile."))

        self.setScale(4, 5)

        # build up package list if necessary
        if tui.includePackages:
            try:
                rhnreg.sendPackages(systemId, tui.selectedPackages)
            except up2dateErrors.CommunicationError, e:
                FatalErrorWindow(self.screen, _("Problem sending package list:\n") + e.errmsg)
            except:
                log.log_exception(*sys.exc_info())
                FatalErrorWindow(self.screen, _("Problem sending package list."))

        rhnreg.startRhnsd()

        self.setScale(5, 5)
        
        # Review Window
        rw = ReviewWindow(self.screen, self.tui, reg_info)
        rw_results = rw.run()

        # Pop the pwin (Progress bar window)
        self.screen.popWindow()

    def setScale(self, amount, total):
        self.scale.set(int(((amount * 1.0)/ total) * 100))
        self.pwin.draw()
        self.screen.refresh()


    def saveResults(self):
        pass


    def run(self):
        log.log_debug("Running %s" % self.__class__.__name__)
        result = self.g.runOnce()
        button = self.bb.buttonPressed(result)

        if result == "F12":
            return "next"
        return button

class ReviewWindow:

    def __init__(self, screen, tui, reg_info):
        self.name = "ReviewWindow"
        self.screen = screen
        self.tui = tui
        self.reg_info = reg_info
        size = snack._snack.size()
        
        toplevel = snack.GridForm(screen, REVIEW_WINDOW, 1, 2)
    
        # Build up the review_window_text based on the data in self.reg_info
        review_window_text = REVIEW_WINDOW_PROMPT + "\n\n"
        
        if self.tui.other['registration_number']:
            review_window_text += SUBSCRIPTIONS + "\n"

            # Test if we successfully activated an installation number
            if self.tui.activate_result.getStatus() == \
               rhnreg.ActivationResult.ACTIVATED_NOW:
                
                # Say we activated the #, and what it activated.
                review_window_text += SUB_NUM % \
                                      self.tui.other['registration_number'] + "\n\n"

                channels = self.tui.activate_result.getChannelsActivated()
                system_slots = self.tui.activate_result.getSystemSlotsActivated()
                log.log_debug('channels is %s' % channels)
                log.log_debug('slots is %s' % system_slots)

                seen = 0
                text = ""
                for channel in channels.keys():
                    seen = 1
                    text += channel + _(", quantity:") + \
                            str(channels[channel]) + "\n"

                for system_slot in system_slots.keys():
                    seen = 1
                    text += system_slot + _(", quantity:") + \
                            str(system_slots[system_slot]) + "\n"

                if seen:
                    review_window_text += SUB_NUM_RESULT + "\n\n"
                    review_window_text += text + "\n\n"

            # This is the case where we read the num from disk and it was
            # already activated.
            elif self.tui.activate_result.getStatus() == \
                 rhnreg.ActivationResult.ALREADY_USED and \
                 self.tui.read_reg_num:
                  review_window_text += INST_NUM_ON_DISK + "\n\n"

        elif self.tui.read_reg_num and len(self.tui.read_reg_num) > 0:
            # If we get here, it means we read a # off disk, but it wasn't a
            # valid num
            review_window_text += INST_NUM_ON_DISK_NA + "\n\n"
            
        # Create and add the text for what channels the system was
        # subscribed to.
        if len(self.reg_info['channels']) > 0:
            channel_list = ""
            for channel in self.reg_info['channels']:
                channel_list += channel + "\n"

            channels = CHANNELS_TITLE + "\n" + \
                       OK_CHANNELS + "\n" + \
                       "%s\n" 

            # If it's hosted, reference the hosted url,
            # otherwise, we don't know the url for their sat.
            log.log_debug("server type is %s " % self.tui.serverType)
            if self.tui.serverType == 'hosted':
                channels += CHANNELS_HOSTED_WARNING
            else:
                channels += CHANNELS_SAT_WARNING

            review_window_text += channels % channel_list + "\n\n"
            
        if len(self.reg_info['system_slots']) > 0:
            slot_list = ""
            for slot in self.reg_info['system_slots']:
                if slot == 'enterprise_entitled':
                    slot_list += MANAGEMENT + "\n"
                elif slot == 'provisioning_entitled':
                    slot_list += PROVISIONING + "\n"
                elif slot == 'sw_mgr_entitled':
                    slot_list += UPDATES + "\n"
                elif slot == 'monitoring_entitled':
                    slot_list += MONITORING + "\n"
                else:
                    slot_list += slot + "\n"
            review_window_text += SLOTS % slot_list + "\n\n"
            
        if len(self.reg_info['universal_activation_key']) > 0:
            act_key_list = ""
            for act_key in self.reg_info['universal_activation_key']:
                act_key_list += act_key
            review_window_text += ACTIVATION_KEY % (act_key_list)
            
        self.review_window = snack.Textbox(size[0]-10, size[1]-14, review_window_text, 1, 1)
    
        toplevel.add(self.review_window, 0, 0, padding = (0, 1, 0, 0))
        
        # BUTTON BAR
        self.bb = snack.ButtonBar(screen, [(OK, "ok")])
        toplevel.add(self.bb, 0, 1, padding = (0, 1, 0, 0),
                     growx = 1)

        self.g = toplevel

    def saveResults(self):
        return 1

    def run(self):
        log.log_debug("Running %s" % self.__class__.__name__)
        result = self.g.runOnce()
        button = self.bb.buttonPressed(result)

        if result == "F12":
            return "ok"
            
        return button    
    
class Tui:

    def __init__(self, screen):
        self.screen = screen
        self.size = snack._snack.size()
        self.drawFrame()
        self.alreadyRegistered = 0
        self.hasMultipleOrgs = 0
        self.orgs = None
        self.default_org = None
        try:
            self.serverType = rhnreg.getServerType()
        except up2dateErrors.InvalidProtocolError:
            FatalErrorWindow(screen, _("You specified an invalid protocol." +
                                     "Only https and http are allowed."))

        self.windows = [
            ConnectWindow,
            StartWindow,
            InfoWindow,
            OrgGroupWindow,
            SubscriptionWindow,
            HardwareWindow,
            PackagesWindow,
            SendWindow,
            FinishWindow
            ]

        # if serverUrl is a list in the config, only reference the first one
        # when we need it
        if type(cfg['serverURL']) == type([]):
            self.serverURL = cfg['serverURL'][0]
        else:
            self.serverURL = cfg['serverURL']
       
    def __del__(self):
        self.screen.finish()


    def drawFrame(self):
        self.welcomeText = COPYRIGHT_TEXT
        self.screen.drawRootText(0, 0, self.welcomeText)
        self.screen.pushHelpLine(_("  <Tab>/<Alt-Tab> between elements  |  <Space> selects  |  <F12> next screen"))


    def initResults(self):
        self.userName = ""
        self.password = ""
        self.email = ""

        self.oemInfo = {}
        self.productInfo = {
            "entitlement_num" : "",
            "registration_num" : "",
            "first_name" : "",
            "last_name" : "",
            "company" : "",
            "address" : "",
            "city" : "",
            "state" : "",
            "zip" : "",
            "country" : "",
           }

        self.activate_result = {}           
        self.invalid_num_on_disk = 0
        self.other = {} 
        self.other['registration_number'] = ''
        
        self.profileName = ""
        self.includeHardware = 1
        self.hostname = ""
        self.ip = ""
        self.cpu = ""
        self.speed = 0
        self.ram = ""
        self.os_release = ""
        self.activated_now = 0
        
        self.includePackages = 0
        self.packageList = []
        self.selectedPackages = []
        self.read_reg_num = None

        self.saw_sub_window = 0
        self.saw_org_window = 0

        
    def run(self):
        log.log_debug("Running %s" % self.__class__.__name__)
        self.initResults()
        
        try:
            index = 0
            while index < len(self.windows):

                win = self.windows[index](self.screen, self)
                    
                # Don't offer group selection screen if the user is not 
                # a member of multiple groups.
                log.log_debug("index is %s" % index)
                log.log_debug("win.name is %s, hasMutlipleGroups is %s" % \
                              (win.name, self.hasMultipleOrgs))
                
                if win.name == 'OrgGroupWindow':
                    if not (self.hasMultipleOrgs and \
                            self.serverType == 'hosted'):
                        index = index + 1
                        continue

                if win.name == 'SubscriptionWindow':

                    # Don't show the subscription window if we're running 
                    # against satellite.
                    if self.serverType == 'satellite':
                        index = index + 1
                        continue
                        
                    # Read the IN # off disk and activate it. 
                    self.read_reg_num = rhnreg.readRegNum()
                    # Store the # if we got one back
                    if self.read_reg_num != None and len(self.read_reg_num) > 0:
                        
                        # Activate the #
                        # Only send up org_id if it exists.
                        try:
                            if self.other.has_key('org_id'):
                                self.activate_result = \
                                             rhnreg.activateRegistrationNumber(
                                             self.userName, self.password, 
                                             self.read_reg_num,
                                             self.other['org_id'])
                            else:
                                self.activate_result = \
                                             rhnreg.activateRegistrationNumber(
                                             self.userName, self.password, 
                                             self.read_reg_num)

                            # We got past the registration, so save the read
                            # reg num as the installation number for this
                            # registration.
                            self.other['registration_number'] = \
                                                              self.read_reg_num

                            if self.activate_result.getStatus() == \
                               rhnreg.ActivationResult.ACTIVATED_NOW:
                                self.activated_now = 1

                        except up2dateErrors.InvalidRegistrationNumberError:
                            self.invalid_num_on_disk = 1
                        except up2dateErrors.NotEntitlingError:
                            pass

                    
                    # Read the IN # from the bios and activate it.
                    activateHWResult = None
                    hardwareInfo = None
                    try:
                        hardwareInfo = hardware.get_hal_system_and_smbios()
                    except:
                        log.log_me("There was an error while reading the hardware info from "
                                   "the bios. Traceback:\n")
                        log.log_exception(*sys.exc_info())

                    if hardwareInfo:
                        try:
                            # Only send up org_id if it exists.
                            if self.other.has_key('org_id'):
                                activateHWResult = rhnreg.activateHardwareInfo(self.userName, self.password, 
                                                          hardwareInfo, self.other['org_id'])
                            else:
                                activateHWResult = rhnreg.activateHardwareInfo(self.userName, self.password, 
                                                          hardwareInfo)
                            if activateHWResult.getStatus() == rhnreg.ActivationResult.ACTIVATED_NOW:
                                self.read_reg_num_hw = activateHWResult.getRegistrationNumber()
                                self.other['registration_number'] = self.read_reg_num_hw
                                self.activated_now = 1
                        except up2dateErrors.NotEntitlingError:
                            log.log_debug('There are are no entitlements associated with this '
                                          'hardware.')

                    # Don't show the subscription window if we have
                    # subscriptions available.
                    try: 
                        subs = rhnreg.getRemainingSubscriptions(self.userName,
                            self.password)
                    except up2dateErrors.NoBaseChannelError, e:
                        subs = 0

                    if int(subs) > 0:
                        log.log_debug('we still have subscriptions %s' % \
                                      str(subs))


                        if self.saw_sub_window == 0:

                            index = index + 1
                            continue

                result = win.run()

                if result == "back":

                    # hardware window
                    if win.name == 'HardwareWindow': # and self.alreadyRegistered:

                        # If we saw the sub window, go back 1
                        if self.saw_sub_window == 1:
                            index = index - 1
                        # Else, if we saw the org window, go back 2
                        elif self.saw_org_window == 1:
                            index = index - 2
                        # Else, we must not have seen either go back 3
                        else:
                            index = index - 3

                    elif win.name == 'SubscriptionWindow':
                        # If we didn't see the org window, go back 2
                        if self.saw_org_window == 0:
                            index = index - 2
                    else:
                        index = index - 1
                elif result == "cancel":
                    log.log_debug("Caught a cancel request")
                    
                    # Show the confirm quit window
                    if ConfirmQuitWindow(self.screen) == 1:
                        return
                    
                    # if we returned from the window, increment the index
                    # index = index + 1
                    
                elif result == "next":
                    index = index + 1
                    win.saveResults()

        finally:
            self.screen.finish()

        
def main():
    test = 0    
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    if len(sys.argv) > 1:
        if sys.argv[1] == "-t" or sys.argv[1] == "--test":
            test = 1
    # cfg['development'] is the newer and hopefully better way to run in 
    # development mode
    if cfg['development']:
        cfg['debug'] = 2
        # Disable logging to terminal because tui will be there. I hope setting
        # this to false doesn't break anything.
        cfg['isatty'] = False
        cfg['debugtofile'] = True
    
    screen = snack.SnackScreen()

    if geteuid() != 0 and not test and not cfg['development']:
        FatalErrorWindow(screen, _("You must run the RHN registration program as root."))


    if rhnreg.registered() and not test:


        systemIdXml = rpclib.xmlrpclib.loads(up2dateAuth.getSystemId())
        oldUsername = systemIdXml[0][0]['username']
        oldsystemId = systemIdXml[0][0]['system_id']
        if type(cfg['serverURL']) == type([]):
            oldserver = cfg['serverURL'][0]
        else:
            oldserver = cfg['serverURL']

        if snack.ButtonChoiceWindow(screen, 
                                    _("System software updates already set up"),
                                    SYSTEM_ALREADY_REGISTERED + 
                                    _("\n\nRed Hat Network Location: ") + 
                                    oldserver +
                                    _("\nRHN Login: ") + oldUsername +
                                    _("\nSystem ID: ") + oldsystemId,
                                    buttons = [YES_CONT, NO_CANCEL],
                                    width = 75,
                                    ) == string.lower(NO_CANCEL):
            
            screen.finish()
            sys.exit(1)
        
    tui = Tui(screen)
    tui.run()

    
if __name__ == "__main__":
    main()
