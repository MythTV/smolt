#!/usr/bin/python
# -*- coding: utf-8 -*-
 
# Copyright (C) 2009 Carlos Gonçalves <mail@cgoncalves.info>
# Copyright (C) 2009 Sebastian Pipping <sebastian@pipping.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
 
import sys
import os
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from urlparse import urljoin
 
from i18n import _
import smolt
import smolt_config
import gui
import privacypolicy
from optparse import OptionParser
from gate import GateFromConfig
import time

debug = False
server_url = None

if os.path.exists(os.path.join(sys.path[0], 'Makefile')):
	CLIENT_PATH = sys.path[0] + '/'
else:
	CLIENT_PATH = '/usr/share/smolt/client/'

class GatherThread(QThread):
	def __init__(self, parent=None):
		self.hardware = None
		self.error_message = None
		QThread.__init__(self, parent)

	def run(self):
		if debug:
			time.sleep(5)
		try:
			self.hardware = smolt.Hardware()
			try:
				smolt.getPubUUID()
				self.emit(SIGNAL('smoltPageStatus(PyQt_PyObject)'), True)
			except:
				self.emit(SIGNAL('smoltPageStatus(PyQt_PyObject)'), False)
			self.emit(SIGNAL('profile_ready()'))
		except smolt.SystemBusError, e:
			self.error_message = e.msg
			self.emit(SIGNAL('system_bus_error()'))
		except smolt.UUIDError, e:
			self.error_message = e.msg
			self.emit(SIGNAL('system_bus_error()'))

class SubmitThread(QThread):
	def __init__(self, hardware, parent=None):
		self.hardware = hardware
		QThread.__init__(self, parent)

	def run(self):
		global server_url
		try:
			time_before = time.time()
			retvalue, self.pub_uuid, self.admin = \
				self.hardware.send(smoonURL=server_url)
			time_after = time.time()
			duration_seconds = time_after - time_before
			if retvalue == 0:
				print 'Submission took %d seconds' % duration_seconds
				self.emit(SIGNAL('submission_completed()'))
			else:
				print 'Submission failed after %d seconds' % duration_seconds
				self.emit(SIGNAL('submission_failed()'))
		except TypeError:
			self.emit(SIGNAL('submission_failed()'))


class SmoltGui(QMainWindow):
 
	def __init__(self):
 
		''' Main Window '''
		QMainWindow.__init__(self)
		self.setMinimumSize(500, 600)
		self.setWindowTitle(_('Smolt'))
		self.setWindowIcon(QIcon(os.path.join(CLIENT_PATH, 'icons', 'smolt.png')))
 
		''' Menu Bar '''
		self.menuBar = self.menuBar()
		self.fileMenu = self.menuBar.addMenu(_('&File'))
		self.helpMenu = self.menuBar.addMenu(_('&Help'))
 
		''' Actions '''
		self.sendAction= QAction(QIcon(os.path.join(CLIENT_PATH, 'icons', 'send-profile.png')), _('&Send Profile'), self)
		self.mySmoltPageAction = QAction(QIcon(os.path.join(CLIENT_PATH, 'icons', 'home.png')), _('&My Smolt Page'), self)
		self.exitAction = QAction(QIcon(os.path.join(CLIENT_PATH, 'icons', 'exit.png')), _('&Exit'), self)
		self.showPPAction = QAction(QIcon(os.path.join(CLIENT_PATH, 'icons', 'privacy.png')), _('Show &Privacy Policy'), self)
		self.aboutAction = QAction(QIcon(os.path.join(CLIENT_PATH, 'icons', 'smolt.png')), _('&About'), self)
		self.aboutQtAction = QAction(_("About &Qt"), self)
 
		''' Fill Menus '''
		self.fileMenu.addAction(self.sendAction)
		self.fileMenu.addAction(self.mySmoltPageAction)
		self.fileMenu.addSeparator()
		self.fileMenu.addAction(self.exitAction)
 
		self.helpMenu.addAction(self.showPPAction)
		self.helpMenu.addSeparator()
		self.helpMenu.addAction(self.aboutAction)
		self.helpMenu.addAction(self.aboutQtAction)
 
		''' Tool Bar '''
		self.toolBar = self.addToolBar(_('Main Tool Bar'))
		self.toolBar.setIconSize(QSize(24, 24))
		self.toolBar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
		self.toolBar.addAction(self.sendAction)
		self.toolBar.addAction(self.mySmoltPageAction)
		self.toolBar.addAction(self.showPPAction)
		self.toolBar.addAction(self.exitAction)
 
		''' Central Widget '''
		self.central = QWidget(self)
		self.mainLayout = QGridLayout()
		
		''' Tabs '''
		self.host_table = gui.HostTable()
		self.device_table = gui.DeviceTable()
		self.generalTab = gui.GeneralTab(self.host_table, self.device_table)

		self.distroTab = gui.DistroTab()
		self.distroInfo = QTextBrowser()
		self.distroInfo.setReadOnly(True)
		self.distroTab.addWidget(self.distroInfo)

		self.mainTabWidget = gui.MainTabWidget(self.generalTab, self.distroTab)
		self.mainLayout.addWidget(self.mainTabWidget)
		self.central.setLayout(self.mainLayout)
		self.setCentralWidget(self.central)
 
		''' Connectors ''' 
		self.connect(self.sendAction, SIGNAL('triggered()'), self.sendProfile)
		self.connect(self.mySmoltPageAction, SIGNAL('triggered()'), self.openSmoltPage)
		self.connect(self.exitAction, SIGNAL('triggered()'), SLOT('close()'))
		self.connect(self.showPPAction, SIGNAL('triggered()'), self.showPP)
		self.connect(self.aboutAction, SIGNAL('triggered()'), self.about)
		self.connect(self.aboutQtAction, SIGNAL("triggered()"), qApp, SLOT("aboutQt()"))

		self.adjustSize()

		self._gather_data()

	def _on_gathering_completed(self):
		self.time_line.stop()
		self.time_line = None
		self.progress_dialog.setValue(100)
		self.progress_dialog = None

	def _on_profile_ready(self):
		self._on_gathering_completed()
		self.host_table.set_profile(self._gather_thread.hardware)
		self.device_table.set_profile(self._gather_thread.hardware)
		self.distro_document = QTextDocument()
		self.distro_document.setHtml(_('No distribution-specific data yet'))
		self.distroInfo.setDocument(self.distro_document)

	def _on_system_bus_error(self):
		self._on_gathering_completed()
		QMessageBox(QMessageBox.Critical, _('Error'),
				self._gather_thread.error_message,
				QMessageBox.Ok, self).exec_()
		QCoreApplication.exit(1)

	def _setup_progress_dialog(self, label=None, force_show=True):
		self.progress_dialog = QProgressDialog(label, '', 0, 100, self);
		self.progress_dialog.setCancelButton(None)
		self.progress_dialog.setWindowTitle('Smolt')
		self.progress_dialog.setWindowModality(Qt.WindowModal);
		self.progress_dialog.setValue(0)
		if force_show:
			self.progress_dialog.forceShow()
		else:
			self.progress_dialog.setMinimumDuration(1)

	def _setup_progress_animation(self, duration_seconds):
		self.time_line = QTimeLine(duration_seconds)
		self.time_line.setUpdateInterval(500)
		self.time_line.setFrameRange(0, 99)
		self.time_line.setCurveShape(QTimeLine.EaseOutCurve)
		self.connect(self.time_line, SIGNAL('frameChanged(int)'), \
			self.progress_dialog, SLOT('setValue(int)'))
		self.time_line.start()

	def _gather_data(self):
		self._setup_progress_dialog(label='Gathering data...', force_show=False)
		# TODO get live progress instead?
		self._setup_progress_animation(5000)

		self._gather_thread = GatherThread()
		self.connect(self._gather_thread, SIGNAL("profile_ready()"), \
			self._on_profile_ready)
		self.connect(self._gather_thread, SIGNAL("system_bus_error()"), \
			self._on_system_bus_error)
		self.connect(self._gather_thread, SIGNAL('smoltPageStatus(PyQt_PyObject)'), \
			self._smoltPageStatus)

		self._gather_thread.start()

	def sendProfile(self):
		self._setup_progress_dialog(label='Sending profile...', force_show=True)
		# TODO take size of data to submit into account?
		self._setup_progress_animation(smolt.timeout * 1000)

		self._submit_thread = SubmitThread(self._gather_thread.hardware)
		self.connect(self._submit_thread, SIGNAL('submission_failed()'), \
			self._on_submission_failed)
		self.connect(self._submit_thread, SIGNAL('submission_completed()'), \
			self._on_submission_completed)
		self._submit_thread.start()

	def _tear_progress_down(self, success=False):
		self.time_line.stop()
		self.time_line = None
		if success:
			self.progress_dialog.setValue(100)
		else:
			self.progress_dialog.cancel()
		self.progress_dialog = None

	def _on_submission_failed(self):
		self._tear_progress_down(success=False)
		QMessageBox(QMessageBox.Critical, _('Error'),
				_('An error occurred while sending the data to the server.'),
				QMessageBox.Ok, self).exec_()

	def _on_submission_completed(self):
		global server_url
		self._tear_progress_down(success=True)
		url = smolt.get_profile_link(server_url, self._submit_thread.pub_uuid)
		admin_password = self._submit_thread.admin
		QMessageBox(QMessageBox.Information, _('Profile Sent'),
				_('<b>Your profile was sent successfully!</b><br>\
				<br>\
				Your profiles is available online at:<br>\
				<a href="%(url)s">%(url)s</a><br>\
				<br>\
				Your profile admin password is:<br><i>%(password)s</i>') % \
					{'url':url, 'password':admin_password},
				QMessageBox.NoButton, self).exec_()

		self._smoltPageStatus(True)

	def _smoltPageStatus(self, enable):
			self.mySmoltPageAction.setEnabled(enable)

	def openSmoltPage(self):
		global server_url

		''' Open My Smolt Page '''
		url = smolt.get_profile_link(server_url, smolt.getPubUUID())
		QDesktopServices.openUrl(QUrl(url))
 
	def showPP(self):
 
		''' Show Privacy Policy '''
		self.privacyPolicy = QMessageBox(QMessageBox.NoIcon, _('Privacy Policy'),
					QString(privacypolicy.PRIVACY_POLICY), QMessageBox.Close, self)
		self.privacyPolicy.exec_()
 
	def about(self):
 
		''' About Smolt and Smolt Qt Client '''
		about = QDialog(self)
		about.setWindowTitle("About Smolt Qt")
		layout = QGridLayout(about)
 
		label = QLabel(self)
		label.setPixmap(QPixmap(os.path.join(CLIENT_PATH, 'icons' , 'smolt.png')))
 
		title = QString(_("<h3>Smolt Qt</h3>Version %(version)s<br/>") % {'version':smolt.clientVersion})
		title.append(_("<br/>Smolt Qt is a Smolt GUI client to submit Smolt hardware profiles \
				to a Smoon server.<br/>"))
 
		description = QString(_("<b>About Smolt:</b><br/>The smolt hardware profiler is a server-client \
				system that does a hardware scan against a machine and sends the results \
				to a public Fedora Project turbogears server. The sends are anonymous \
				and should not contain any private information other than the physical \
				hardware information and basic OS info.<br/>"))
 
		authors = _("<b>Authors:</b><br/>Carlos Gonçalves &lt;mail@cgoncalves.info&gt;")
 
		lbl = QLabel(_("%(title)s<br>\
				%(description)s<br>\
				%(authors)s<br>\
				<br>\
				<b>License:</b><br>\
				This program is free software; you can redistribute it and/or \
				modify it under the terms of the GNU General Public License \
				as published by the Free Software Foundation; either version 3 \
				of the License, or (at your option) any later version.") % \
				{'title':title, 'description':description, 'authors':authors})
 
		lbl.setWordWrap(True)
		lbl.setOpenExternalLinks(True)
 
		buttonBox = QDialogButtonBox(QDialogButtonBox.Close);
		about.connect(buttonBox , SIGNAL('rejected()'), about, SLOT('reject()'));
		about.connect(label, SIGNAL('triggered()'), about, SLOT('accept()'));
 
		layout.addWidget(label, 0, 0, 1, 1);
		layout.addWidget(lbl, 0, 1, 4, 4);
		layout.addWidget(buttonBox, 4, 2, 1, 1);
 
		about.exec_()

if __name__ == '__main__':
    dollar_zero_backup = sys.argv[0]
    parser = OptionParser(version = smolt.clientVersion)
    parser.add_option('--config',
                    dest = 'the_only_config_file',
                    default = None,
                    metavar = 'file.cfg',
                    help = _('specify the location of the (only) config file to use'))
    parser.add_option('-s', '--server',
                    dest = 'smoonURL',
                    default = smolt.smoonURL,
                    metavar = 'smoonURL',
                    help = _('specify the URL of the server (default "%default")'))
    (opts, args) = parser.parse_args()
    server_url = opts.smoonURL
    if opts.the_only_config_file != None:
        GateFromConfig(opts.the_only_config_file)

    # NOTE: Run "python smoltGui.py --foo -- --one --two"
    # to set args passed to Qt to ['--one', '--two']
    app = QApplication([dollar_zero_backup] + args)
    smolt_gui = SmoltGui()
    smolt_gui.show()
    sys.exit(app.exec_())
