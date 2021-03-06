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
Thread to copy or move files without blocking the GUI.
"""

import os
import shutil
from ..qt import QtCore


class ProcessFilesThread(QtCore.QThread):
    """
    Thread to process files (copy or move).

    :param source_dir: path to the source directory
    :param destination_dir: path to the destination directory (created if doesn't exist)
    :param move: indicates if the files must be moved instead of copied
    """

    # signals to update the progress dialog.
    error = QtCore.pyqtSignal(str)
    completed = QtCore.pyqtSignal()
    update = QtCore.pyqtSignal(int)

    def __init__(self, source_dir, destination_dir, move=False):

        QtCore.QThread.__init__(self)
        self._source = source_dir
        self._destination = destination_dir
        self._move = move

    def run(self):
        """
        Thread starting point.
        """

        self._is_running = True

        # count the number of files in the source directory
        file_count = self._countFiles(self._source)

        # create the destination directory if it doesn't exist
        if not os.path.exists(self._destination):
            try:
                os.makedirs(self._destination)
            except EnvironmentError as e:
                self.error.emit("Could not create directory {}: {}".format(self._destination, str(e)))
                return

        copied = 0
        # start copying/moving from the source directory
        for path, dirs, filenames in os.walk(self._source):
            base_dir = path.replace(self._source, self._destination)

            # start create the destination sub-directories
            for directory in dirs:
                if not self._is_running:
                    return
                try:
                    destination_dir = os.path.join(base_dir, directory)
                    if not os.path.exists(destination_dir):
                        os.makedirs(destination_dir)
                except EnvironmentError as e:
                    self.error.emit("Could not create directory {}: {}".format(destination_dir, str(e)))
                    return

            # finally the files themselves
            for sfile in filenames:
                if not self._is_running:
                    return
                source_file = os.path.join(path, sfile)
                destination_file = os.path.join(base_dir, sfile)
                try:
                    if self._move:
                        shutil.move(source_file, destination_file)
                    else:
                        shutil.copy2(source_file, destination_file)
                except EnvironmentError as e:
                    pass # FIXME
#                     if self._move:
#                         self.error.emit("Could not move file to {}: {}".format(destination_file, str(e)))
#                     else:
#                         self.error.emit("Could not copy file to {}: {}".format(destination_file, str(e)))
                    return
                copied += 1
                # update the progress made
                progress = float(copied) / file_count * 100
                self.update.emit(progress)

        # everything has been copied or moved, let's inform the GUI before the thread exits
        self.completed.emit()

    def stop(self):
        """
        Stops this thread as soon as possible.
        """

        self._is_running = False

    def _countFiles(self, directory):
        """
        Counts all the files in a directory.

        :param directory: path to the directory.
        """

        count = 0
        for _, _, files in os.walk(directory):
            count += len(files)
        return count
