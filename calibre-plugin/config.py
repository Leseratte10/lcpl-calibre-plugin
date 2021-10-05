#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pyright: reportUndefinedVariable=false


from PyQt5.Qt import (QWidget, QHBoxLayout, QVBoxLayout, QGroupBox)

from PyQt5 import Qt as QtGui
from zipfile import ZipFile

# modules from this plugin's zipfile.
import calibre_plugins.lcplinput.prefs as prefs                                 # type: ignore


class ConfigWidget(QWidget):
    def __init__(self, plugin_path):
        QWidget.__init__(self)

        self.plugin_path = plugin_path

        # get the prefs
        self.lcplinputprefs = prefs.LCPLInput_Prefs()

        # make a local copy
        self.templcplinputprefs = {}
        self.templcplinputprefs['useragent'] = self.lcplinputprefs['useragent']
        self.templcplinputprefs['use_custom_ua'] = self.lcplinputprefs['use_custom_ua']
        self.templcplinputprefs['ignore_content_errors'] = self.lcplinputprefs['ignore_content_errors']
        self.templcplinputprefs['honor_license_time_limits'] = self.lcplinputprefs['honor_license_time_limits']


        # Start Qt Gui dialog layout
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        ua_group_box = QGroupBox(_('User-Agent:'), self)
        layout.addWidget(ua_group_box)
        ua_group_box_layout = QVBoxLayout()
        ua_group_box.setLayout(ua_group_box_layout)

        self.chkDefaultUA = QtGui.QCheckBox(_("Use custom User-Agent"))
        self.chkDefaultUA.setToolTip(_("Enter User Agent for book downloads"))
        self.chkDefaultUA.setChecked(self.templcplinputprefs['use_custom_ua'])
        self.chkDefaultUA.stateChanged.connect(self.chkUAchanged)
        ua_group_box_layout.addWidget(self.chkDefaultUA)

        self.txtboxUA = QtGui.QLineEdit(self)
        self.txtboxUA.setToolTip(_("Enter User Agent for book downloads"))
        self.txtboxUA.setText(self.templcplinputprefs['useragent'])
        self.txtboxUA.setEnabled(self.chkDefaultUA.isChecked())
        ua_group_box_layout.addWidget(self.txtboxUA)



        other_group_box = QGroupBox(_('Other settings:'), self)
        layout.addWidget(other_group_box)
        other_group_box_layout = QVBoxLayout()
        other_group_box.setLayout(other_group_box_layout)

        self.chkIgnoreErrors = QtGui.QCheckBox(_("Ignore LCP content errors"))
        self.chkIgnoreErrors.setToolTip(_("Default: False \n\nIf this is enabled, errors in the LCPL file (wrong size, wrong hash, etc.) are ignored. May result in invalid or corrupted files."))
        self.chkIgnoreErrors.setChecked(self.templcplinputprefs['ignore_content_errors'])
        other_group_box_layout.addWidget(self.chkIgnoreErrors)

        self.chkHonorTimeLimits = QtGui.QCheckBox(_("Honor license validity timeframe"))
        self.chkHonorTimeLimits.setToolTip(_("Default: True \n\nSome LCP licenses, like from a library, are only valid in a certain timeframe. \nIf you *disable* this setting you can make the tool ignore that timeframe so you can download expired books \nbut the server might notice and get you banned if you disable this setting.\nAlso, there's no guarantee that the book is even still available on the server for you."))
        self.chkHonorTimeLimits.setChecked(self.templcplinputprefs['honor_license_time_limits'])
        other_group_box_layout.addWidget(self.chkHonorTimeLimits)



        self.resize(self.sizeHint())

    def chkUAchanged(self):
        self.txtboxUA.setEnabled(self.chkDefaultUA.isChecked())



    def save_settings(self):
        self.lcplinputprefs.set('useragent', self.txtboxUA.text())
        self.lcplinputprefs.set('use_custom_ua', self.chkDefaultUA.isChecked())
        self.lcplinputprefs.set('ignore_content_errors', self.chkIgnoreErrors.isChecked())
        self.lcplinputprefs.set('honor_license_time_limits', self.chkHonorTimeLimits.isChecked())

        if (self.txtboxUA.text() == ""):
            self.lcplinputprefs.set('use_custom_ua', False)

        self.lcplinputprefs.writeprefs()

    def load_resource(self, name):
        with ZipFile(self.plugin_path, 'r') as zf:
            if name in zf.namelist():
                return zf.read(name).decode('utf-8')
        return ""

