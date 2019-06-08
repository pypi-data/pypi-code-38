############################################################
# -*- coding: utf-8 -*-
#
# MOUNTCONTROL
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PyQT5 for python
# Python  v3.6.5
#
# Michael Würtenberger
# (c) 2018
#
# Licence APL2.0
#
############################################################
# standard libraries
import logging
import socket
# external packages
import PyQt5.QtCore
import PyQt5.QtWidgets
# local imports
import mountcontrol.mount


__all__ = ['Mount',
           ]


class WorkerSignals(PyQt5.QtCore.QObject):
    """
    The WorkerSignals class offers a list of signals to be used and instantiated by the
    Worker class to get signals for error, finished and result to be transferred to the
    caller back
    """

    __all__ = ['WorkerSignals']
    version = '0.1'

    finished = PyQt5.QtCore.pyqtSignal()
    error = PyQt5.QtCore.pyqtSignal(object)
    result = PyQt5.QtCore.pyqtSignal(object)


class Worker(PyQt5.QtCore.QRunnable):
    """
    The Worker class offers a generic interface to allow any function to be executed as a
    thread in an threadpool
    """

    __all__ = ['Worker',
               'run']
    version = '0.1'
    logger = logging.getLogger(__name__)

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        # the worker signal must not be a class variable, but instance otherwise
        # we get trouble when having multiple threads running
        self.signals = WorkerSignals()

    def run(self):
        """
        runs an arbitrary methods with it's parameters and catches the result

        :return: nothing, but sends results and status as signals
        """

        try:
            result = self.fn(*self.args, **self.kwargs)
        except Exception as e:
            self.signals.error.emit(e)
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()


class MountSignals(PyQt5.QtCore.QObject):
    """
    The MountSignals class offers a list of signals to be used and instantiated by
    the Mount class to get signals for triggers for finished tasks to
    enable a gui to update their values transferred to the caller back.

    This has to be done in a separate class as the signals have to be subclassed from
    QObject and the Mount class itself is subclassed from object
    """

    __all__ = ['MountSignals']
    version = '0.5'

    pointDone = PyQt5.QtCore.pyqtSignal(object)
    settDone = PyQt5.QtCore.pyqtSignal(object)
    alignDone = PyQt5.QtCore.pyqtSignal(object)
    namesDone = PyQt5.QtCore.pyqtSignal(object)
    fwDone = PyQt5.QtCore.pyqtSignal(object)
    locationDone = PyQt5.QtCore.pyqtSignal(object)
    mountUp = PyQt5.QtCore.pyqtSignal(bool)
    slewFinished = PyQt5.QtCore.pyqtSignal()
    alert = PyQt5.QtCore.pyqtSignal()


class Mount(mountcontrol.mount.Mount):
    """
    The Mount class is the main interface for interacting with the mount computer.
    The user could:
        setup / change the interface to the mount
        start / stop cyclic tasks to poll data from mount
        send and get data from mount
        has signals for interfacing to external GUI's for data updates

        >>> settings = Mount(
        >>>                     host=host,
        >>>                     MAC=MAC,
        >>>                     pathToData=pathToData,
        >>>                     expire=expire,
        >>>                     verbose=verbose,
        >>>                 )

    """

    CYCLE_POINTING = 500
    CYCLE_MOUNT_UP = 1000
    CYCLE_SETTING = 3000

    # set timeout
    SOCKET_TIMEOUT = 0.1

    def __init__(self,
                 host=None,
                 MAC=None,
                 pathToData=None,
                 expire=None,
                 verbose=None,
                 ):

        super().__init__(host=host,
                         MAC=MAC,
                         pathToData=pathToData,
                         expire=expire,
                         verbose=verbose,
                         )

        self._settlingTime = 0

        self.statusAlert = False
        self.statusSlew = True

        # signal handling
        self.signals = MountSignals()
        self.threadPool = PyQt5.QtCore.QThreadPool()
        self.mutexMountUp = PyQt5.QtCore.QMutex()
        self.mutexPointing = PyQt5.QtCore.QMutex()
        self.mutexSetting = PyQt5.QtCore.QMutex()
        self.mutexGetAlign = PyQt5.QtCore.QMutex()
        self.mutexGetNames = PyQt5.QtCore.QMutex()
        self.mutexGetFW = PyQt5.QtCore.QMutex()
        self.mutexGetLocation = PyQt5.QtCore.QMutex()
        self.mutexWorkaround = PyQt5.QtCore.QMutex()
        # timers
        self.timerPointing = PyQt5.QtCore.QTimer()
        self.timerPointing.setSingleShot(False)
        self.timerPointing.timeout.connect(self.cyclePointing)
        self.timerSetting = PyQt5.QtCore.QTimer()
        self.timerSetting.setSingleShot(False)
        self.timerSetting.timeout.connect(self.cycleSetting)
        self.timerMountUp = PyQt5.QtCore.QTimer()
        self.timerMountUp.setSingleShot(False)
        self.timerMountUp.timeout.connect(self.cycleCheckMountUp)
        self.settlingWait = PyQt5.QtCore.QTimer()
        self.settlingWait.setSingleShot(True)
        self.settlingWait.timeout.connect(self.waitSettlingAndEmit)

    @property
    def settlingTime(self):
        return self._settlingTime * 1000

    @settlingTime.setter
    def settlingTime(self, value):
        self._settlingTime = value

    def waitSettlingAndEmit(self):
        """
        waitSettlingAndEmit emit the signal for slew finished

        :return: true for test purpose
        """

        self.signals.slewFinished.emit()

        return True

    def startTimers(self):
        """
        startTimers enables the cyclic timers for polling necessary mount data.

        :return: nothing
        """

        self.timerSetting.start(self.CYCLE_SETTING)
        self.timerPointing.start(self.CYCLE_POINTING)
        self.timerMountUp.start(self.CYCLE_MOUNT_UP)

    def stopTimers(self):
        """
        stopTimers disables the cyclic timers for polling necessary mount data.
        in addition wait for threadPool to finish

        :return: nothing
        """

        self.timerPointing.stop()
        self.timerSetting.stop()
        self.timerMountUp.stop()
        self.threadPool.waitForDone()

    def shutdown(self):
        """

        :return:
        """

        suc = self.obsSite.shutdown()
        self.mountUp = False
        return suc

    def resetData(self):
        """
        resetData deletes all data already stored in classes just by redefining the
        classes. it send as well a signal, when the data is cleared.

        :return: nothing
        """

        super().resetData()
        self.signals.pointDone.emit(self.obsSite)
        self.signals.settDone.emit(self.sett)
        self.signals.alignDone.emit(self.model)
        self.signals.namesDone.emit(self.model)
        self.signals.fwDone.emit(self.fw)
        self.signals.locationDone.emit(self.obsSite.location)

    def checkMountUp(self):
        """
        checkMountUp polls the host/port of the mount computer and set the state and
        signals for the status accordingly.

        :return: nothing
        """

        socket.setdefaulttimeout(self.SOCKET_TIMEOUT)
        client = socket.socket()
        client.settimeout(self.SOCKET_TIMEOUT)
        try:
            client.connect(self.host)
        except Exception:
            if self.mountUp:
                self.mountUp = False
            client.close()
        else:
            if not self.mountUp:
                self.mountUp = True
            client.shutdown(socket.SHUT_RDWR)
            client.close()
        finally:
            pass

    def errorCycleCheckMountUp(self, e):
        """
        the cyclic or long lasting tasks for getting date from the mount should not run
        twice for the same data at the same time. so there is a mutex to prevent this
        behaviour. remove the mutex unlock this mutex.

        :return: nothing
        """

        self.logger.error(f'Cycle error: {e}')

    def clearCycleCheckMountUp(self):
        """
        the cyclic or long lasting tasks for getting date from the mount should not run
        twice for the same data at the same time. so there is a mutex to prevent this
        behaviour. remove the mutex unlock this mutex.

        :return: nothing
        """

        self.mutexMountUp.unlock()
        self.signals.mountUp.emit(self.mountUp)

    def cycleCheckMountUp(self):
        """
        cycleCheckMountUp prepares the worker thread and the signals for getting the settings
        data.

        :return: nothing
        """

        if not self.mutexMountUp.tryLock():
            self.logger.info('overrun in check mount up')
            self.signals.mountUp.emit(self.mountUp)
            return

        worker = Worker(self.checkMountUp)
        worker.signals.finished.connect(self.clearCycleCheckMountUp)
        worker.signals.error.connect(self.errorCycleCheckMountUp)
        self.threadPool.start(worker)

    def errorCyclePointing(self, e):
        """
        the cyclic or long lasting tasks for getting date from the mount should not run
        twice for the same data at the same time. so there is a mutex to prevent this
        behaviour. remove the mutex unlock this mutex.

        :return: nothing
        """
        self.logger.error(f'Cycle error: {e}')

    def clearCyclePointing(self):
        """
        the cyclic or long lasting tasks for getting date from the mount should not run
        twice for the same data at the same time. so there is a mutex to prevent this
        behaviour. remove the mutex unlock this mutex.

        :return: nothing
        """

        # test for certain conditions
        # if  has emergency stop, emit warning
        if self.obsSite.status in [1, 98, 99]:
            if not self.statusAlert:
                self.signals.alert.emit()
            self.statusAlert = True
        else:
            self.statusAlert = False

        # if stop slewing, emit warning
        if self.obsSite.status not in [2, 6, 6]:
            if not self.statusSlew:
                # start timer for settling time and emit signal afterwards
                self.settlingWait.start(self.settlingTime)
            self.statusSlew = True
        else:
            self.statusSlew = False

        self.mutexPointing.unlock()
        self.signals.pointDone.emit(self.obsSite)

    def cyclePointing(self):
        """
        cyclePointing prepares the worker thread and the signals for getting the pointing
        data.

        :return: nothing
        """

        if not self.mountUp:
            self.signals.pointDone.emit(self.obsSite)
            return
        if not self.mutexPointing.tryLock():
            self.logger.info('overrun in pointing')
            # self.logger.info('threads: {0}'.format(self.threadPool.activeThreadCount()))
            self.signals.pointDone.emit(self.obsSite)
            return
        worker = Worker(self.obsSite.pollPointing)
        worker.signals.finished.connect(self.clearCyclePointing)
        worker.signals.error.connect(self.errorCyclePointing)
        self.threadPool.start(worker)

    def errorCycleSetting(self, e):
        """
        the cyclic or long lasting tasks for getting date from the mount should not run
        twice for the same data at the same time. so there is a mutex to prevent this
        behaviour. remove the mutex unlock this mutex.

        :return: nothing
        """
        self.logger.error(f'Cycle error: {e}')

    def clearCycleSetting(self):
        """
        the cyclic or long lasting tasks for getting date from the mount should not run
        twice for the same data at the same time. so there is a mutex to prevent this
        behaviour. remove the mutex unlock this mutex.

        :return: nothing
        """

        self.mutexSetting.unlock()
        self.signals.settDone.emit(self.sett)

    def cycleSetting(self):
        """
        cycleSet prepares the worker thread and the signals for getting the settings
        data.

        :return: nothing
        """

        if not self.mountUp:
            self.signals.settDone.emit(self.sett)
            return
        if not self.mutexSetting.tryLock():
            self.logger.info('overrun in setting')
            self.signals.settDone.emit(self.sett)
            return
        worker = Worker(self.sett.pollSetting)
        worker.signals.finished.connect(self.clearCycleSetting)
        worker.signals.error.connect(self.errorCycleSetting)
        self.threadPool.start(worker)

    def errorGetAlign(self, e):
        """
        the cyclic or long lasting tasks for getting date from the mount should not run
        twice for the same data at the same time. so there is a mutex to prevent this
        behaviour. remove the mutex unlock this mutex.

        :return: nothing
        """
        self.logger.error(f'Cycle error: {e}')

    def clearGetAlign(self):
        """
        the cyclic or long lasting tasks for getting date from the mount should not run
        twice for the same data at the same time. so there is a mutex to prevent this
        behaviour. remove the mutex unlock this mutex.

        :return: nothing
        """

        self.mutexGetAlign.unlock()
        self.signals.alignDone.emit(self.model)

    def getAlign(self):
        """
        getAlign prepares the worker thread and the signals for getting the alignment model
        data.

        :return: nothing
        """

        if not self.mountUp:
            self.signals.alignDone.emit(self.model)
            return
        if not self.mutexGetAlign.tryLock():
            self.logger.info('overrun in getAlign')
            self.signals.alignDone.emit(self.model)
            return
        worker = Worker(self.model.pollStars)
        worker.signals.finished.connect(self.clearGetAlign)
        worker.signals.error.connect(self.errorGetAlign)
        self.threadPool.start(worker)

    def errorGetNames(self, e):
        """
        the cyclic or long lasting tasks for getting date from the mount should not run
        twice for the same data at the same time. so there is a mutex to prevent this
        behaviour. remove the mutex unlock this mutex.

        :return: nothing
        """
        self.logger.error(f'Cycle error: {e}')

    def clearGetNames(self):
        """
        the cyclic or long lasting tasks for getting date from the mount should not run
        twice for the same data at the same time. so there is a mutex to prevent this
        behaviour. remove the mutex unlock this mutex.

        :return: nothing
        """

        self.mutexGetNames.unlock()
        self.signals.namesDone.emit(self.model)

    def getNames(self):
        """
        getNames prepares the worker thread and the signals for getting the alignment model
        names.

        :return: nothing
        """

        if not self.mountUp:
            self.signals.namesDone.emit(self.model)
            return
        if not self.mutexGetNames.tryLock():
            self.logger.info('overrun in getNames')
            self.signals.namesDone.emit(self.model)
            return
        worker = Worker(self.model.pollNames)
        worker.signals.finished.connect(self.clearGetNames)
        worker.signals.error.connect(self.errorGetNames)
        self.threadPool.start(worker)

    def errorGetFW(self, e):
        """
        the cyclic or long lasting tasks for getting date from the mount should not run
        twice for the same data at the same time. so there is a mutex to prevent this
        behaviour. remove the mutex unlock this mutex.

        :return: nothing
        """
        self.logger.error(f'Cycle error: {e}')

    def clearGetFW(self):
        """
        the cyclic or long lasting tasks for getting date from the mount should not run
        twice for the same data at the same time. so there is a mutex to prevent this
        behaviour. remove the mutex unlock this mutex.

        :return: nothing
        """

        self.mutexGetFW.unlock()
        self.signals.fwDone.emit(self.fw)

    def getFW(self):
        """
        getFW prepares the worker thread and the signals for getting the build data of
        the mount computer.

        :return: nothing
        """

        if not self.mountUp:
            self.signals.fwDone.emit(self.fw)
            return
        if not self.mutexGetFW.tryLock():
            self.logger.info('overrun in getFW')
            self.signals.fwDone.emit(self.fw)
            return
        worker = Worker(self.fw.poll)
        worker.signals.finished.connect(self.clearGetFW)
        worker.signals.error.connect(self.errorGetFW)
        self.threadPool.start(worker)

    def errorGetLocation(self, e):
        """
        the cyclic or long lasting tasks for getting date from the mount should not run
        twice for the same data at the same time. so there is a mutex to prevent this
        behaviour. remove the mutex unlock this mutex.

        :return: nothing
        """
        self.logger.error(f'Cycle error: {e}')

    def clearGetLocation(self):
        """
        the cyclic or long lasting tasks for getting date from the mount should not run
        twice for the same data at the same time. so there is a mutex to prevent this
        behaviour. remove the mutex unlock this mutex.

        :return: nothing
        """

        self.mutexGetLocation.unlock()
        self.signals.locationDone.emit(self.obsSite.location)

    def getLocation(self):
        """
        getLocation prepares the worker thread and the signals for getting the mount
        location data.

        :return: nothing
        """

        if not self.mountUp:
            self.signals.locationDone.emit(self.obsSite.location)
            return
        if not self.mutexGetLocation.tryLock():
            self.logger.info('overrun in getLocation')
            self.signals.locationDone.emit(self.obsSite.location)
            return
        worker = Worker(self.obsSite.getLocation)
        worker.signals.finished.connect(self.clearGetLocation)
        worker.signals.error.connect(self.errorGetLocation)
        self.threadPool.start(worker)
