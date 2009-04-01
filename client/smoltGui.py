#!/usr/bin/python
# -*- coding: utf-8 -*-
 
# Copyright (C) 2009 Carlos Gonçalves <mail@cgoncalves.info>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
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
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from urlparse import urljoin
 
#sys.path.append('/home/carlos/devel/smolt/qt')
 
from i18n import _
import smolt
import gui
import privacypolicy
 
class SmoltGui(QMainWindow):
 
	def __init__(self):
 
		''' Main Window '''
		QMainWindow.__init__(self)
		self.profile = smolt.Hardware()
		self.resize(500, 600)
		self.setWindowTitle(_('Smolt'))
		self.setWindowIcon(QIcon('icons/smolt.png'))
 
		''' Menu Bar '''
		self.menuBar = self.menuBar()
		self.fileMenu = self.menuBar.addMenu(_('&File'))
		self.helpMenu = self.menuBar.addMenu(_('&Help'))
 
		''' Actions '''
		self.sendAction= QAction(QIcon('icons/mail-message-new.png'), _('&Send Profile'), self)
		self.mySmoltPageAction = QAction(QIcon('icons/go-home.png'), _('&My Smolt Page'), self)
		self.exitAction = QAction(QIcon('icons/application-exit.png'), _('&Exit'), self)
		self.showPPAction = QAction(QIcon('icons/dialog-information.png'), _('Show &Privacy Policy'), self)
		self.aboutAction = QAction(QIcon('icons/smolt.png'), _('&About'), self)
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
		self.toolBar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
		self.toolBar.addAction(self.sendAction)
		self.toolBar.addAction(self.mySmoltPageAction)
		self.toolBar.addAction(self.showPPAction)
		self.toolBar.addAction(self.exitAction)
 
		''' Central Widget '''
		self.central = QWidget(self)
		self.mainLayout = QGridLayout()
		self.mainLayout.addWidget(gui.HostTable(self.profile).get())
		self.mainLayout.addWidget(gui.DeviceTable(self.profile).get())
		self.central.setLayout(self.mainLayout)
		self.setCentralWidget(self.central)
 
		''' Connectors ''' 
		self.connect(self.sendAction, SIGNAL('triggered()'), self.sendProfile)
		self.connect(self.mySmoltPageAction, SIGNAL('triggered()'), self.openSmoltPage)
		self.connect(self.exitAction, SIGNAL('triggered()'), SLOT('close()'))
		self.connect(self.showPPAction, SIGNAL('triggered()'), self.showPP)
		self.connect(self.aboutAction, SIGNAL('triggered()'), self.about)
		self.connect(self.aboutQtAction, SIGNAL("triggered()"), qApp, SLOT("aboutQt()"))
 
	def sendProfile(self):
 
		''' Send the profile to the smolt server '''
		import smolt
		try:
			retvalue, pub_uuid, admin = self.profile.send(smoonURL=smolt.smoonURL)
			url = urljoin(smolt.smoonURL, '/show?uuid=%s' % pub_uuid)
			finishMessage = QMessageBox(QMessageBox.Information, _('Profile Sent'),
					_('The data was successfully sent. If you need to refer to your hardware profile for a bug report your UUID is \n%s\nstored in %s') \
						% (url, smolt.get_config_attr("HW_UUID", "/etc/sysconfig/hw-uuid")),
					QMessageBox.NoButton, self)
			success = True
		except TypeError:
			finishMessage = QMessageBox(QMessageBox.Warning, _('Error'),
					_('An error occurred while sending the data to the server.'),
					QMessageBox.Ok, self)
 
		finishMessage.exec_()
		if success is True:
			QDesktopServices.openUrl(QUrl(url))
 
	def openSmoltPage(self):
 
		''' Open My Smolt Page '''
		import smolt
		retvalue, pub_uuid, admin = self.profile.send(smoonURL=smolt.smoonURL)
	        QDesktopServices.openUrl(QUrl(urljoin(smolt.smoonURL, '/show?uuid=%s' % pub_uuid)))
 
	def showPP(self):
 
		''' Show Privacy Policy '''
		self.privacyPolicy = QMessageBox(QMessageBox.NoIcon, _('Privacy Policy'),
					privacypolicy.PRIVACY_POLICY, QMessageBox.Close, self)
		self.privacyPolicy.exec_()
 
	def about(self):
 
		''' About Smolt and Smolt Qt Client '''
		about = QDialog(self)
		about.setWindowTitle("About Smolt Qt")
		layout = QGridLayout(about)
 
		label = QLabel(self)
		label.setPixmap(QPixmap("icons/smolt.png"))
 
		title = QString(_("<h3>Smolt Qt</h3>Version 0.1.1<br/>"))
		title.append(_("<br/>Smolt Qt is a Smolt GUI client to submit Smolt hardware profiles \
				to a Smoon server.<br/>"))
 
		description = _("<b>About Smolt:</b><br/>The smolt hardware profiler is a server-client \
				system that does a hardware scan against a machine and sends the results \
				to a public Fedora Project turbogears server. The sends are anonymous \
				and should not contain any private information other than the physical \
				hardware information and basic OS info.<br/>")
 
		authors = _("<b>Authors:</b><br/>Carlos Gon&ccedil;alves &lt;mail@cgoncalves.info&gt;")
 
		lbl = QLabel(_("%s<br/>%s<br/>%s<br/><br/><b>License:</b><br/>This program is free software; \
				you can redistribute it and/or modify it under the terms of the GNU General \
				Public License as published by the Free Software Foundation; either version 3 \
				of the License, or (at your option) any later version.") % (title, description, authors))
 
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
	app = QApplication(sys.argv)
	smolt = SmoltGui()
	smolt.show()
	sys.exit(app.exec_())

