# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 GNS3 Technologies Inc.
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

"""
Configuration page for IOU preferences.
"""

import os
import sys
from gns3.qt import QtGui
from gns3.servers import Servers
from .. import IOU
from ..ui.iou_preferences_page_ui import Ui_IOUPreferencesPageWidget
from ..settings import IOU_SETTINGS


class IOUPreferencesPage(QtGui.QWidget, Ui_IOUPreferencesPageWidget):
    """
    QWidget preference page for IOU.
    """

    def __init__(self):

        QtGui.QWidget.__init__(self)
        self.setupUi(self)

        if not sys.platform.startswith("linux"):
            self.uiIouyapPathLineEdit.setEnabled(False)
            self.uiIouyapPathToolButton.setEnabled(False)
            self.uiUseLocalServercheckBox.setEnabled(False)

        # connect signals
        self.uiIOURCPathToolButton.clicked.connect(self._iourcPathBrowserSlot)
        self.uiIouyapPathToolButton.clicked.connect(self._iouyapPathBrowserSlot)
        self.uiRestoreDefaultsPushButton.clicked.connect(self._restoreDefaultsSlot)
        self.uiUseLocalServercheckBox.stateChanged.connect(self._useLocalServerSlot)
        self.uiTestSettingsPushButton.clicked.connect(self._testSettingsSlot)

    def _iourcPathBrowserSlot(self):
        """
        Slot to open a file browser and select an iourc file
        """

        path = QtGui.QFileDialog.getOpenFileName(self, "Select the IOURC file", ".")
        if not path:
            return

        if not os.access(path, os.R_OK):
            QtGui.QMessageBox.critical(self, "IOURC file", "{} cannot be read".format(os.path.basename(path)))
            return

        self.uiIOURCPathLineEdit.setText(os.path.normpath(path))

    def _iouyapPathBrowserSlot(self):
        """
        Slot to open a file browser and select iouyap.
        """

        path = QtGui.QFileDialog.getOpenFileName(self, "Select iouyap", ".")
        if not path:
            return

        if not os.access(path, os.X_OK):
            QtGui.QMessageBox.critical(self, "iouyap", "{} is not an executable".format(os.path.basename(path)))
            return

        self.uiIouyapPathLineEdit.setText(os.path.normpath(path))

    def _testSettingsSlot(self):

        QtGui.QMessageBox.critical(self, "Test settings", "Sorry, not yet implemented!")

    def _restoreDefaultsSlot(self):
        """
        Slot to populate the page widgets with the default settings.
        """

        self._populateWidgets(IOU_SETTINGS)

    def _useLocalServerSlot(self, state):
        """
        Slot to enable or not the QTreeWidget for remote servers.
        """

        if state:
            self.uiRemoteServersTreeWidget.setEnabled(False)
        else:
            self.uiRemoteServersTreeWidget.setEnabled(True)

    def _populateWidgets(self, settings):
        """
        Populates the widgets with the settings.

        :param settings: IOU settings
        """

        self.uiIOURCPathLineEdit.setText(settings["iourc"])
        self.uiIouyapPathLineEdit.setText(settings["iouyap"])
        self.uiUseLocalServercheckBox.setChecked(settings["use_local_server"])
        self.uiConsoleStartPortSpinBox.setValue(settings["console_start_port_range"])
        self.uiConsoleEndPortSpinBox.setValue(settings["console_end_port_range"])
        self.uiUDPStartPortSpinBox.setValue(settings["udp_start_port_range"])
        self.uiUDPEndPortSpinBox.setValue(settings["udp_end_port_range"])

    def _updateRemoteServersSlot(self):
        """
        Adds/Updates the available remote servers.
        """

        servers = Servers.instance()
        self.uiRemoteServersTreeWidget.clear()
        for server in servers.remoteServers().values():
            host = server.host
            port = server.port
            item = QtGui.QTreeWidgetItem(self.uiRemoteServersTreeWidget)
            item.setText(0, host)
            item.setText(1, str(port))

        self.uiRemoteServersTreeWidget.resizeColumnToContents(0)

    def loadPreferences(self):
        """
        Loads IOU preferences.
        """

        iou_settings = IOU.instance().settings()
        self._populateWidgets(iou_settings)

        servers = Servers.instance()
        servers.updated_signal.connect(self._updateRemoteServersSlot)
        self._updateRemoteServersSlot()

    def savePreferences(self):
        """
        Saves IOU preferences.
        """

        new_settings = {}
        new_settings["iourc"] = self.uiIOURCPathLineEdit.text()
        new_settings["iouyap"] = self.uiIouyapPathLineEdit.text()
        new_settings["use_local_server"] = self.uiUseLocalServercheckBox.isChecked()
        new_settings["console_start_port_range"] = self.uiConsoleStartPortSpinBox.value()
        new_settings["console_end_port_range"] = self.uiConsoleEndPortSpinBox.value()
        new_settings["udp_start_port_range"] = self.uiUDPStartPortSpinBox.value()
        new_settings["udp_end_port_range"] = self.uiUDPEndPortSpinBox.value()
        IOU.instance().setSettings(new_settings)
