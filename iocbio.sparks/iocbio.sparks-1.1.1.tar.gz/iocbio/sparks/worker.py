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
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#  Copyright (C) 2018
#   Laboratory of Systems Biology, Department of Cybernetics,
#   School of Science, Tallinn University of Technology
#  Authors: Martin Laasmaa and Marko Vendelin
#  This file is part of project: IOCBIO Sparks
#
import PyQt5.QtCore as QC
from PyQt5.QtCore import pyqtSlot, pyqtSignal

workPool = None

class JobSignals(QC.QObject):
    sigJobDone = pyqtSignal()

class Job(QC.QRunnable):
    """Job interface"""

    def __init__(self, pool=None):
        QC.QRunnable.__init__(self)
        if pool is None:
            pool = workPool
        self.job_id = pool.get_id()
        self.pool = pool
        self._job_signals = JobSignals()

    def run(self):
        if not self.pool.expired(self.job_id):
            self.run_job()
        self._job_signals.sigJobDone.emit()

    def expired(self):
        return self.pool.expired(self.job_id)

    def start(self):
        self.pool.start(self)


class Pool(QC.QObject):

    sigJobNumberChanged = pyqtSignal(int)

    def __init__(self):
        QC.QObject.__init__(self)

        self.workPool = QC.QThreadPool()
        self.active_jobs = 0

        self.current_id = 0
        self.expired_id = 0

        # running several minpack optimizations in parallel leads to crash
        # see https://github.com/scipy/scipy/commit/05028ff66eadeee32b33ac2f994c009093355534
        self.workPool.setMaxThreadCount(1)

    def jobs(self):
        return self.active_jobs

    def start(self, runnable):
        self.active_jobs += 1
        runnable._job_signals.sigJobDone.connect(self._job_done)
        self.workPool.start(runnable)
        self.sigJobNumberChanged.emit(self.active_jobs)

    def get_id(self):
        i = self.current_id
        self.current_id = i + 1
        return i

    def expired(self, i):
        return (i < self.expired_id)

    def drop_all(self):
        self.expired_id = self.current_id

    def _job_done(self):
        self.active_jobs -= 1
        self.sigJobNumberChanged.emit(self.active_jobs)

    def disconnect(self):
        self.sigJobNumberChanged.disconnect()
