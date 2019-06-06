import logging
from typing import Callable, Optional, List, Dict

import os
import re
import shutil
from collections import namedtuple
from twisted.internet import reactor
from watchdog.events import FileSystemEventHandler, FileMovedEvent, FileModifiedEvent, \
    FileDeletedEvent, FileCreatedEvent

logger = logging.getLogger(__name__)

# Quiten the file watchdog
logging.getLogger("watchdog.observers.inotify_buffer").setLevel(logging.INFO)

SyncFileHookCallable = Callable[[str, bytes], bytes]

FileSyncCfg = namedtuple('FileSyncCfg',
                         ['srcDir', 'dstDir', 'parentMustExist',
                          'deleteExtraDstFiles',
                          'keepCompiledFilePatterns',
                          'preSyncCallback', 'postSyncCallback',
                          'excludeFilesRegex'])

from watchdog.utils import platform

if platform.is_darwin():
    """
    Don't use fsevents as it only monitors a file once.
    This caused problems when syncing one directory to multiple targets, 
    such as from a peek plugin to build-web and build-ns
    
    # from watchdog.observers.fsevents import FSEventsObserver as WatchdogObserver
    """

    # FIXME: catching too broad. Error prone
    try:
        from watchdog.observers.polling import PollingObserver as WatchdogObserver

        logger.debug("We're on macOS, Forcing kqueue")

    except:
        logger.warning("Failed to import kqueue. Fall back to Watchdogs default.")
        from watchdog.observers import Observer as WatchdogObserver

else:
    from watchdog.observers import Observer as WatchdogObserver


class FrontendFileSync:
    """ Peek App Frontend File Sync

    This class is used to syncronise the frontend files from the plugins into the 
        frontend build dirs.

    """

    def __init__(self, syncFileHookCallable: SyncFileHookCallable):
        self._syncFileHookCallable = syncFileHookCallable
        self._dirSyncMap = list()
        self._fileWatchdogObserver = None

    def addSyncMapping(self, srcDir, dstDir,
                       parentMustExist=False,
                       deleteExtraDstFiles=True,
                       preSyncCallback: Optional[Callable[[], None]] = None,
                       postSyncCallback: Optional[Callable[[], None]] = None,
                       keepCompiledFilePatterns: Optional[Dict[str, List[str]]] = None,
                       excludeFilesRegex: List[str] = ()):
        """ Add Sync Mapping
        
        :param srcDir: The source dir to sync files from
        
        :param dstDir: The dest dir to sync files to
        
        :param parentMustExist: The parent must exist for file syncing to happen.
                If it doesn't syncing quitely doesn't occur.
                
        :param deleteExtraDstFiles: If there are additional files in the dest directory
                that are not in the source directory, then delete them.
                
        :param keepCompiledFilePatterns:
                A dict of key = src file extension, val = an array of extensions to keep
                for this src file extension.

                EG {'ts', ['js.map', 'js']}
                A list of extensions to keep if we are syncing over a file with that name.
                For example, if we're syncing over thing.ts and another process compiles
                thing.ts into thing.js in the same directory, we should not delete
                thing.js next time we start.

                If this is a TS file and we want to keep dest .js and .js.map files
                 then add them to our srcFiles list, this

                The reason being, the JS files will be deleted because they don't
                 exist in the source, which causes nativescript to rebuild FOR EVERY
                .js file delete
                
        :param preSyncCallback: This will be called before syncing occurs.
                This include any incremental syncing.
                
        :param postSyncCallback: This will be called after syncing occurs.
                This includes any incremental syncing.

        :param excludeFilesRegex: If the relative path+filename match this regexp then
                            the file is not incldued in the syncing.
        
        """
        if not keepCompiledFilePatterns:
            keepCompiledFilePatterns = {}

        self._dirSyncMap.append(
            FileSyncCfg(srcDir, dstDir, parentMustExist,
                        deleteExtraDstFiles,
                        keepCompiledFilePatterns,
                        preSyncCallback, postSyncCallback,
                        excludeFilesRegex)
        )

    def startFileSyncWatcher(self):
        self._fileWatchdogObserver = WatchdogObserver()

        for cfg in self._dirSyncMap:
            self._fileWatchdogObserver.schedule(
                _FileChangeHandler(self._syncFileHookCallable, cfg),
                cfg.srcDir, recursive=True)

        self._fileWatchdogObserver.start()

        reactor.addSystemEventTrigger('before', 'shutdown', self.stopFileSyncWatcher)
        logger.debug("Started frontend file watchers")

    def stopFileSyncWatcher(self):
        self._fileWatchdogObserver.stop()
        self._fileWatchdogObserver.join()
        self._fileWatchdogObserver = None
        logger.debug("Stopped frontend file watchers")

    def syncFiles(self):

        for cfg in self._dirSyncMap:
            parentDstDir = os.path.dirname(cfg.dstDir)
            if cfg.parentMustExist and not os.path.isdir(parentDstDir):
                logger.debug("Skipping sink, parent doesn't exist. dstDir=%s", cfg.dstDir)
                continue

            if cfg.preSyncCallback:
                cfg.preSyncCallback()

            # Create lists of files relative to the dstDir and srcDir
            existingFiles = set(self._listFiles(cfg.dstDir))
            srcFiles = set(self._listFiles(cfg.srcDir))
            destCompiledFiles = set()

            for regexp in cfg.excludeFilesRegex:
                rexp = re.compile(regexp)
                srcFiles = set(filter(lambda l: not rexp.match(l), srcFiles))

            for srcFile in srcFiles:
                srcFilePath = os.path.join(cfg.srcDir, srcFile)
                dstFilePath = os.path.join(cfg.dstDir, srcFile)

                # If this is a TS file and we want to keep dest .js and .js.map files
                # then add them to our srcFiles list, this

                if '.' in srcFile:
                    srcFileNoExt, srcFileExt = srcFile.rsplit('.', 1)
                else:
                    srcFileNoExt, srcFileExt = srcFile, ''

                if srcFileExt in cfg.keepCompiledFilePatterns:
                    for ext in cfg.keepCompiledFilePatterns[srcFileExt]:
                        destCompiledFiles.add("%s.%s" % (srcFileNoExt, ext))

                dstFileDir = os.path.dirname(dstFilePath)
                os.makedirs(dstFileDir, exist_ok=True)
                self._fileCopier(srcFilePath, dstFilePath)

            if cfg.deleteExtraDstFiles:
                for obsoleteFile in existingFiles - srcFiles - destCompiledFiles:
                    obsoleteFile = os.path.join(cfg.dstDir, obsoleteFile)

                    if os.path.islink(obsoleteFile):
                        os.remove(obsoleteFile)

                    elif os.path.isdir(obsoleteFile):
                        shutil.rmtree(obsoleteFile)

                    else:
                        os.remove(obsoleteFile)

            if cfg.postSyncCallback:
                cfg.postSyncCallback()

    def _writeFileIfRequired(self, dir, fileName, contents):
        fullFilePath = os.path.join(dir, fileName)

        # Since writing the file again changes the date/time,
        # this messes with the self._recompileRequiredCheck
        if os.path.isfile(fullFilePath):
            with open(fullFilePath, 'r') as f:
                if contents == f.read():
                    logger.debug("%s is up to date", fileName)
                    return

        logger.debug("Writing new %s", fileName)

        with open(fullFilePath, 'w') as f:
            f.write(contents)

    def _fileCopier(self, src, dst):
        with open(src, 'rb') as f:
            contents = f.read()

        contents = self._syncFileHookCallable(dst, contents)

        # If the contents hasn't change, don't write it
        if os.path.isfile(dst):
            with open(dst, 'rb') as f:
                if f.read() == contents:
                    return

        with open(dst, 'wb') as f:
            f.write(contents)

    def _listFiles(self, dir):
        ignoreFiles = set('.lastHash')
        paths = []
        for (path, directories, filenames) in os.walk(dir):

            for filename in filenames:
                if filename in ignoreFiles:
                    continue
                paths.append(os.path.join(path[len(dir) + 1:], filename))

        return paths


class _FileChangeHandler(FileSystemEventHandler):
    def __init__(self, syncFileHook, cfg: FileSyncCfg):
        self._syncFileHook = syncFileHook
        self._srcDir = cfg.srcDir
        self._dstDir = cfg.dstDir
        self._cfg = cfg

        self._rexp = [re.compile(r) for r in cfg.excludeFilesRegex]

    def _makeSrcFileRelPath(self, srcFilePath: str) -> str:
        return srcFilePath[len(self._srcDir):]

    def _makeDestPath(self, srcFilePath: str) -> str:
        return self._dstDir + self._makeSrcFileRelPath(srcFilePath)

    def _updateFileContents(self, srcFilePath):

        relativeSrcFilePath = self._makeSrcFileRelPath(srcFilePath)
        for r in self._rexp:
            if r.match(relativeSrcFilePath):
                return

        parentDstDir = os.path.dirname(self._dstDir)
        if self._cfg.parentMustExist and not os.path.isdir(parentDstDir):
            logger.debug("Skipping sync, parent doesn't exist. dstDir=%s", self._dstDir)
            return

        if self._cfg.preSyncCallback:
            self._cfg.preSyncCallback()

        # if the file had vanished, then do nothing
        if not os.path.exists(srcFilePath):
            return

        dstFilePath = self._makeDestPath(srcFilePath)

        # Copy files this way to ensure we only make one file event on the dest side.
        # tns in particular reloads on every file event.

        # This used to be done by copying the file,
        #   then _syncFileHook would modify it in place

        with open(srcFilePath, 'rb') as f:
            contents = f.read()

        contents = self._syncFileHook(dstFilePath, contents)

        # If the contents hasn't change, don't write it
        if os.path.isfile(dstFilePath):
            with open(dstFilePath, 'rb') as f:
                if f.read() == contents:
                    return

        logger.debug("Syncing %s -> %s", srcFilePath[len(self._srcDir) + 1:],
                     self._dstDir)

        # if the dest dir doesn't exist, then create it
        dstDir = os.path.dirname(dstFilePath)
        if not os.path.isdir(dstDir):
            os.makedirs(dstDir, mode=0o755, exist_ok=True)

        # Write the contents
        with open(dstFilePath, 'wb') as f:
            f.write(contents)

        if self._cfg.postSyncCallback:
            self._cfg.postSyncCallback()

    def on_created(self, event):
        if not isinstance(event, FileCreatedEvent) or event.src_path.endswith("__"):
            return

        self._updateFileContents(event.src_path)

    def on_deleted(self, event):
        if not isinstance(event, FileDeletedEvent) or event.src_path.endswith("__"):
            return

        # If the file still exists, then do nothing. This can occur on macOS
        if os.path.exists(event.src_path):
            return

        dstFilePath = self._makeDestPath(event.src_path)

        if os.path.exists(dstFilePath):
            os.remove(dstFilePath)

        # If this is a typescript file, make sure we remove the associated js and js.map
        # files.
        if dstFilePath.endswith(".ts"):
            jsFile = dstFilePath[:-3] + ".js"
            if os.path.exists(jsFile):
                os.remove(jsFile)

            jsMapFile = dstFilePath[:-3] + ".js.map"
            if os.path.exists(jsMapFile):
                os.remove(jsMapFile)

        logger.debug("Removing %s -> %s", event.src_path[len(self._srcDir) + 1:],
                     self._dstDir)

    def on_modified(self, event):
        if not isinstance(event, FileModifiedEvent) or event.src_path.endswith("__"):
            return

        self._updateFileContents(event.src_path)

    def on_moved(self, event):
        if (not isinstance(event, FileMovedEvent)
            or event.src_path.endswith("__")
            or event.dest_path.endswith("__")):
            return

        self._updateFileContents(event.dest_path)

        oldDestFilePath = self._makeDestPath(event.src_path)
        if os.path.exists(oldDestFilePath):
            os.remove(oldDestFilePath)
