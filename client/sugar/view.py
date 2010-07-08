# Copyright (C) 2010 Sebastian Dziallas
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
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA

import os
import gtk
from gettext import gettext as _

from sugar.graphics import style
from jarabe.controlpanel.sectionview import SectionView

CLASS = 'smolt'
ICON = 'module-smolt'
TITLE = _('Hardware Profile')

class smolt(SectionView):

    def __init__(self, model):
        SectionView.__init__(self)

        self._model = model

        self.set_border_width(style.DEFAULT_SPACING * 2)
        self.set_spacing(style.DEFAULT_SPACING)
        self._group = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)

        scrollwindow = gtk.ScrolledWindow()
        scrollwindow.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.pack_start(scrollwindow, expand=True)
        scrollwindow.show()

        self._vbox = gtk.VBox()
        scrollwindow.add_with_viewport(self._vbox)
        self._vbox.show()
        self.add(scrollwindow)

        self._smolt_submit_profile_handler = None
        self._smolt_delete_profile_handler = None

        label_smolt = gtk.Label(_('Hardware Profile'))
        label_smolt.set_alignment(0, 0)
        self._vbox.pack_start(label_smolt, expand=False)
        label_smolt.show()
        box_smolt = gtk.VBox()
        box_smolt.set_border_width(style.DEFAULT_SPACING * 2)
        box_smolt.set_spacing(style.DEFAULT_SPACING)

        smolt_info = gtk.Label(_("We invite you to create a hardware profile for your computer. "
                                 "Doing so helps software developers to diagnose possible problems. "
                                 "You can submit and then delete your profile by pressing the buttons below. "))
        smolt_info.set_alignment(0, 0)
        smolt_info.set_line_wrap(True)
        smolt_info.show()
        box_smolt.pack_start(smolt_info, expand=False)

        box_submit_profile = gtk.HBox(spacing=style.DEFAULT_SPACING)
        self._submit_profile_button = gtk.Button()
        self._submit_profile_button.set_label(_('Submit Profile'))
        box_submit_profile.pack_start(self._submit_profile_button, expand=False)
        self._submit_profile_button.show()
        box_smolt.pack_start(box_submit_profile, expand=False)
        box_submit_profile.show()

        if os.path.exists(os.getenv("HOME") + '/.smolt/uuiddb.cfg'):
            box_delete_profile = gtk.HBox(spacing=style.DEFAULT_SPACING)
            self._delete_profile_button = gtk.Button()
            self._delete_profile_button.set_label(_('Delete Profile'))
            box_delete_profile.pack_start(self._delete_profile_button, expand=False)
            self._delete_profile_button.show()
            box_smolt.pack_start(box_delete_profile, expand=False)
            box_delete_profile.show()

        box_profile = gtk.HBox(spacing=style.DEFAULT_SPACING)
        label_profile = gtk.Label(_('Profile:'))
        label_profile.set_alignment(1, 0)
        label_profile.modify_fg(gtk.STATE_NORMAL, 
                              style.COLOR_SELECTION_GREY.get_gdk_color())
        box_profile.pack_start(label_profile, expand=False)
        self._group.add_widget(label_profile)
        label_profile.show()
        label_profile_url = gtk.Label(self._model.get_profile_url())
        label_profile_url.set_alignment(0, 0)
        box_profile.pack_start(label_profile_url, expand=False)
        label_profile_url.show()
        box_smolt.pack_start(box_profile, expand=False)
        box_profile.show()

        self._vbox.pack_start(box_smolt, expand=False)
        box_smolt.show()

        self._setup_submit()
        self._setup_policy()

        if os.path.exists(os.getenv("HOME") + '/.smolt/uuiddb.cfg'):
            self._setup_delete()

    def _setup_submit(self):
        self._smolt_submit_profile_handler =  \
                self._submit_profile_button.connect( \
                        'clicked', self.smolt_submit_profile_cb)

    def smolt_submit_profile_cb(self, widget):
        self._model.submit_profile()

    def _setup_delete(self):
        self._smolt_delete_profile_handler =  \
                self._delete_profile_button.connect( \
                        'clicked', self.smolt_delete_profile_cb)

    def smolt_delete_profile_cb(self, widget):
        self._model.delete_profile()

    def _setup_policy(self):
        separator_policy = gtk.HSeparator()
        self._vbox.pack_start(separator_policy, expand=False)
        separator_policy.show()

        vbox_policy = gtk.VBox()
        vbox_policy.set_border_width(style.DEFAULT_SPACING * 2)
        vbox_policy.set_spacing(style.DEFAULT_SPACING)

        expander = gtk.Expander(_("Privacy Policy"))
        expander.connect("notify::expanded", self.policy_expander_cb)
        expander.show()
        vbox_policy.pack_start(expander, expand=True)

        self._vbox.pack_start(vbox_policy, expand=True)
        vbox_policy.show()

    def policy_expander_cb(self, expander, param_spec):
        if expander.get_expanded():
            view_policy = gtk.TextView()
            view_policy.set_editable(False)
            view_policy.get_buffer().set_text(self._model.get_policy())
            view_policy.show()
            expander.add(view_policy)
