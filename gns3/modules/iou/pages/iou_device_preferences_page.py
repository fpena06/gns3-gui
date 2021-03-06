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
Configuration page for IOU image & device preferences.
"""

import os
import sys
from gns3.qt import QtGui
from gns3.servers import Servers
from .. import IOU
from ..ui.iou_device_preferences_page_ui import Ui_IOUDevicePreferencesPageWidget


class IOUDevicePreferencesPage(QtGui.QWidget, Ui_IOUDevicePreferencesPageWidget):
    """
    QWidget preference page for IOU image & device preferences.
    """

    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setupUi(self)

        self._iou_images = {}

        self.uiSaveIOUImagePushButton.clicked.connect(self._iouImageSaveSlot)
        self.uiDeleteIOUImagePushButton.clicked.connect(self._iouImageDeleteSlot)
        self.uiIOUImagesTreeWidget.itemClicked.connect(self._iouImageClickedSlot)
        self.uiIOUImagesTreeWidget.itemSelectionChanged.connect(self._iouImageChangedSlot)
        self.uiIOUPathToolButton.clicked.connect(self._iouImageBrowserSlot)
        self.uiStartupConfigToolButton.clicked.connect(self._startupConfigBrowserSlot)
        self.uiIOUImageTestSettingsPushButton.clicked.connect(self._testSettingsSlot)

    def _iouImageClickedSlot(self, item, column):
        """
        Loads a selected IOU image from the tree widget.

        :param item: selected QTreeWidgetItem instance
        :param column: ignored
        """

        image = item.text(0)
        server = item.text(1)
        key = "{server}:{image}".format(server=server, image=image)
        iou_image = self._iou_images[key]

        self.uiIOUPathLineEdit.setText(iou_image["path"])
        self.uiStartupConfigLineEdit.setText(iou_image["startup_config"])
        self.uiRAMSpinBox.setValue(iou_image["ram"])
        self.uiNVRAMSpinBox.setValue(iou_image["nvram"])

    def _iouImageChangedSlot(self):
        """
        Enables the use of the delete button.
        """

        item = self.uiIOUImagesTreeWidget.currentItem()
        if item:
            self.uiDeleteIOUImagePushButton.setEnabled(True)
        else:
            self.uiDeleteIOUImagePushButton.setEnabled(False)

    def _iouImageSaveSlot(self):
        """
        Adds/Saves an IOU image.
        """

        path = self.uiIOUPathLineEdit.text()
        startup_config = self.uiStartupConfigLineEdit.text()
        nvram = self.uiNVRAMSpinBox.value()
        ram = self.uiRAMSpinBox.value()

        # basename doesn't work on Unix with Windows paths
        if not sys.platform.startswith('win') and len(path) > 2 and path[1] == ":":
            import ntpath
            image = ntpath.basename(path)
        else:
            image = os.path.basename(path)

        #TODO: mutiple remote server
        if IOU.instance().settings()["use_local_server"]:
            server = "local"
        else:
            server = server = next(iter(Servers.instance())).host

        key = "{server}:{image}".format(server=server, image=image)
        item = self.uiIOUImagesTreeWidget.currentItem()

        if key in self._iou_images and item and item.text(0) == image:
            item.setText(0, image)
            item.setText(1, server)
        elif key in self._iou_images:
            return
        else:
            # add a new entry in the tree widget
            item = QtGui.QTreeWidgetItem(self.uiIOUImagesTreeWidget)
            item.setText(0, image)
            item.setText(1, server)
            self.uiIOUImagesTreeWidget.setCurrentItem(item)

        self._iou_images[key] = {"path": path,
                                 "image": image,
                                 "startup_config": startup_config,
                                 "ram": ram,
                                 "nvram": nvram,
                                 "server": server}

        self.uiIOUImagesTreeWidget.resizeColumnToContents(0)
        self.uiIOUImagesTreeWidget.resizeColumnToContents(1)

    def _iouImageDeleteSlot(self):
        """
        Deletes an IOU image.
        """

        item = self.uiIOUImagesTreeWidget.currentItem()
        if item:
            image = item.text(0)
            server = item.text(1)
            key = "{server}:{image}".format(server=server, image=image)
            del self._iou_images[key]
            self.uiIOUImagesTreeWidget.takeTopLevelItem(self.uiIOUImagesTreeWidget.indexOfTopLevelItem(item))

    def _iouImageBrowserSlot(self):
        """
        Slot to open a file browser and select an IOU image.
        """

        #TODO: current directory for IOU image + filter?
        path = QtGui.QFileDialog.getOpenFileName(self, "Select an IOU image", ".", "IOU image (*.bin *.image)")
        if not path:
            return

        if not os.access(path, os.R_OK):
            QtGui.QMessageBox.critical(self, "IOU image", "Cannot read {}".format(path))
            return

        try:
            with open(path, "rb") as f:
                # read the first 7 bytes of the file.
                elf_header_start = f.read(7)
        except EnvironmentError as e:
            QtGui.QMessageBox.critical(self, "IOU image", "Cannot read ELF magic number: {}".format(e))
            return

        # file must start with the ELF magic number, be 32-bit, little endian and have an ELF version of 1
        # normal IOS image are big endian!
        if elf_header_start != b'\x7fELF\x01\x01\x01':
            QtGui.QMessageBox.critical(self, "IOU image", "Sorry, this is not a valid IOU image!")
            return

        self.uiIOUPathLineEdit.clear()
        self.uiIOUPathLineEdit.setText(path)
        self.uiRAMSpinBox.setValue(256)
        self.uiNVRAMSpinBox.setValue(128)

    def _startupConfigBrowserSlot(self):
        """
        Slot to open a file browser and select a startup-config file.
        """

        #TODO: current directory for startup-config + filter?
        path = QtGui.QFileDialog.getOpenFileName(self, "Select a startup configuration", ".")
        if not path:
            return

        if not os.access(path, os.R_OK):
            QtGui.QMessageBox.critical(self, "Startup configuration", "Cannot read {}".format(path))
            return

        self.uiStartupConfigLineEdit.clear()
        self.uiStartupConfigLineEdit.setText(path)

    def _testSettingsSlot(self):

        QtGui.QMessageBox.critical(self, "Test settings", "Sorry, not yet implemented!")

    def loadPreferences(self):
        """
        Loads the IOU image & device preferences.
        """

        self._iou_images.clear()
        self.uiIOUImagesTreeWidget.clear()

        iou_images = IOU.instance().iouImages()
        for iou_image in iou_images.values():
            item = QtGui.QTreeWidgetItem(self.uiIOUImagesTreeWidget)
            item.setText(0, iou_image["image"])
            item.setText(1, iou_image["server"])

        self.uiIOUImagesTreeWidget.resizeColumnToContents(0)
        self.uiIOUImagesTreeWidget.resizeColumnToContents(1)
        self._iou_images.update(iou_images)

    def savePreferences(self):
        """
        Saves the IOU image & device preferences.
        """

        IOU.instance().setIOUImages(self._iou_images)
