import functools
import os.path
import aioipfs
import time

from PyQt5.QtWidgets import QStackedWidget
from PyQt5.QtWidgets import QToolButton
from PyQt5.QtWidgets import QMenu
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QApplication

from PyQt5.QtGui import QKeySequence
from PyQt5.QtGui import QMovie
from PyQt5.QtGui import QIcon

from PyQt5.QtCore import QCoreApplication
from PyQt5.QtCore import QSize
from PyQt5.QtCore import QFile
from PyQt5.QtCore import QFileInfo
from PyQt5.QtCore import QIODevice

from galacteek import ensure
from galacteek import log
from galacteek import logUser

from galacteek.appsettings import CFG_SECTION_BROWSER
from galacteek.appsettings import CFG_KEY_HOMEURL
from galacteek.core.clipboard import ClipboardItem
from galacteek.ipfs.cidhelpers import stripIpfs
from galacteek.ipfs.cidhelpers import isIpnsPath
from galacteek.ipfs.cidhelpers import isIpfsPath
from galacteek.ipfs.cidhelpers import shortPathRepr
from galacteek.ipfs import ipfsOp
from galacteek.ipfs.stat import StatInfo
from galacteek.ipfs import megabytes
from galacteek.ipfs.mimetype import mimeTypeDag
from galacteek.crypto.qrcode import IPFSQrDecoder
from galacteek.crypto.qrcode import IPFSQrEncoder

from .hashmarks import addHashmark
from .helpers import qrCodesMenuBuilder
from .helpers import getMimeIcon
from .helpers import getFavIconFromDir
from .helpers import getIconFromMimeType
from .helpers import getIcon
from .helpers import messageBox
from .helpers import getIconFromImageData
from .helpers import runDialog
from .helpers import disconnectSig
from .helpers import sizeFormat
from .widgets import PopupToolButton
from .widgets import DownloadProgressButton
from .dialogs import ChooseProgramDialog

from . import dag

from .i18n import iUnknown
from .i18n import iDagViewer
from .i18n import iHashmark
from .i18n import iIpfsQrEncode


def iClipboardEmpty():
    return QCoreApplication.translate(
        'clipboardManager',
        'No valid IPFS CID/path in the clipboard')


def iClipboardStackItemsCount(count):
    return QCoreApplication.translate(
        'clipboardManager',
        '{} item(s) in the clipboard stack').format(count)


def iCopyMultihashToClipboard():
    return QCoreApplication.translate(
        'FileManagerForm',
        "Copy multihash to clipboard")


def iCopyPathToClipboard():
    return QCoreApplication.translate(
        'FileManagerForm',
        "Copy full path to clipboard")


def iCopyToClipboard():
    return QCoreApplication.translate(
        'clipboardManager',
        'Copy to clipboard')


def iClipboardNoValidAddress():
    return QCoreApplication.translate(
        'clipboardManager',
        'No valid address for this item')


def iFromClipboard(path):
    return QCoreApplication.translate(
        'clipboardManager',
        'Clipboard: browse IPFS path: {0}').format(path)


def iClipboardClearHistory():
    return QCoreApplication.translate(
        'clipboardManager',
        'Clear clipboard history')


def iClipItemExplore():
    return QCoreApplication.translate('clipboardManager',
                                      'Explore directory')


def iClipItemHashmark():
    return QCoreApplication.translate('clipboardManager',
                                      'Hashmark')


def iClipItemPin():
    return QCoreApplication.translate('clipboardManager',
                                      'Pin')


def iClipItemDownload():
    return QCoreApplication.translate('clipboardManager',
                                      'Download')


def iClipItemIpldExplorer():
    return QCoreApplication.translate('clipboardManager',
                                      'Run IPLD Explorer')


def iClipItemMarkupRocks():
    return QCoreApplication.translate('clipboardManager',
                                      'Open with Markdown editor')


def iClipItemDagView():
    return QCoreApplication.translate('clipboardManager',
                                      'DAG view')


def iClipboardHistory():
    return QCoreApplication.translate('clipboardManager', 'Clipboard history')


def iClipItemBrowse():
    return QCoreApplication.translate('clipboardManager',
                                      'Browse IPFS path')


def iClipItemOpen():
    return QCoreApplication.translate('clipboardManager', 'Open')


def iClipItemOpenWithApp():
    return QCoreApplication.translate('clipboardManager',
                                      'Open with application')


def iClipItemOpenWithDefaultApp():
    return QCoreApplication.translate('clipboardManager',
                                      'Open with default system application')


def iClipItemSetCurrent():
    return QCoreApplication.translate('clipboardManager',
                                      'Set as current clipboard item')


def iClipItemSetAsHome():
    return QCoreApplication.translate('clipboardManager',
                                      'Set as homepage')


def iClipItemRemove():
    return QCoreApplication.translate('clipboardManager',
                                      'Remove item')


def iClipItemSwitch(num):
    return QCoreApplication.translate(
        'clipboardManager',
        'Switch to item {} in the stack').format(num)


def iClipboardStack():
    return QCoreApplication.translate('clipboardManager',
                                      'Clipboard stack')


def iClipStackQrEncrypted():
    return QCoreApplication.translate(
        'clipboardManager',
        'QR codes: encode clipboard stack to image (encrypted)')


def iClipStackQrPublic():
    return QCoreApplication.translate(
        'clipboardManager',
        'QR codes: encode clipboard stack to image (clear)')


class ClipboardManager(PopupToolButton):
    def __init__(self, clipTracker, itemsStack, rscOpener,
                 icon=None, menu=None, parent=None):
        super().__init__(icon=icon, menu=menu, parent=parent,
                         mode=QToolButton.InstantPopup,
                         acceptDrops=True)

        self.app = QApplication.instance()
        self.tracker = clipTracker
        self.itemsStack = itemsStack
        self.rscOpener = rscOpener

        self.setAcceptDrops(True)
        self.setObjectName('clipboardManager')
        self.setToolTip(iClipboardEmpty())

        self.ipfsObjectDropped.connect(self.onIpfsObjectDropped)
        self.fileDropped.connect(self.onFileDropped)

        self.tracker.currentItemChanged.connect(self.itemChanged)
        self.tracker.itemAdded.connect(self.itemAdded)
        self.tracker.itemRemoved.connect(self.itemRemoved)

        self.menu.setToolTipsVisible(True)

        self.itSwitchMenu = QMenu(iClipboardStack())
        self.itSwitchMenu.triggered.connect(self.onItemSwitch)

        self.qrMenu = QMenu(iIpfsQrEncode())
        qrIcon = getIcon('ipfs-qrcode.png')
        self.qrMenu.setIcon(qrIcon)
        self.qrMenu.addAction(qrIcon,
                              iClipStackQrEncrypted(),
                              self.onQrEncodeStackEncrypted)
        self.qrMenu.addAction(qrIcon,
                              iClipStackQrPublic(),
                              self.onQrEncodeStackPublic)

        for num in range(1, 10):
            action = QAction(getIcon('clipboard.png'),
                             iClipItemSwitch(num),
                             self,
                             shortcut=QKeySequence('Ctrl+' + str(num))
                             )
            action.setData(num)
            self.itSwitchMenu.addAction(action)

        self.initHistoryMenu()

    def onItemSwitch(self, action):
        num = action.data()

        if isinstance(num, int):
            button = self.itemsStack.getStackItem(num)
            if button:
                self.tracker.current = button.item

    def initHistoryMenu(self):
        self.menu.clear()

        self.menu.addMenu(self.qrMenu)

        self.menu.addSeparator()
        self.menu.addAction(iClipboardClearHistory(),
                            self.onHistoryClear)
        self.menu.addSeparator()
        self.menu.addMenu(self.itSwitchMenu)

        self.menu.addSeparator()

    def onHistoryClear(self):
        self.initHistoryMenu()
        self.tracker.clearHistory()
        self.updateToolTip()

    def onHistoryItemClicked(self, action):
        item = action.data()

        if item:
            if action.text() == iClipItemOpen():
                ensure(self.rscOpener.open(item.ipfsPath, item.mimeType))
            elif action.text() == iClipItemSetCurrent():
                self.tracker.current = item
            elif action.text() == iClipItemRemove():
                self.tracker.removeItem(item)

    def itemAdded(self, item):
        if isIpnsPath(item.path):
            itemName = item.path

        elif isIpfsPath(item.path):
            itemName = os.path.basename(item.path)
        else:
            itemName = item.path

        nMenu = QMenu(itemName, self)
        nMenu.setToolTipsVisible(True)
        nMenu.setToolTip(item.path)
        nMenu.triggered.connect(self.onHistoryItemClicked)
        self.menu.addMenu(nMenu)

        actionOpen = QAction(iClipItemOpen(), self)
        actionOpen.setToolTip(item.path)
        actionOpen.setData(item)

        actionSetCurrent = QAction(iClipItemSetCurrent(), self)
        actionSetCurrent.setData(item)
        actionSetCurrent.setToolTip(item.path)

        nMenu.addAction(actionOpen)
        nMenu.addAction(actionSetCurrent)

        def changeIcons(item, nMenu, aOpen):
            nMenu.setIcon(item.mimeIcon)
            aOpen.setIcon(item.mimeIcon)

        item.mimeIconAvailable.connect(
            functools.partial(changeIcons, item, nMenu, actionOpen))
        self.updateToolTip()

    def updateToolTip(self):
        self.setToolTip(iClipboardStackItemsCount(len(self.tracker.items)))

    def itemChanged(self, item):
        self.itemsStack.activateItem(item)

    def itemRemoved(self, item):
        self.updateToolTip()

    def onIpfsObjectDropped(self, path):
        """
        Process drag-and-drops of URLs pointing to an IPFS resource

        :param IPFSPath path:
        """
        self.tracker.clipboardProcess(str(path))

    def onFileDropped(self, url):
        ensure(self.dropEventLocalFile(url))

    @ipfsOp
    async def dropEventLocalFile(self, ipfsop, url):
        """
        Handle a drop event with a file:// URL
        """

        maxFileSize = (64 * 1024 * 1024)
        try:
            path = url.toLocalFile()
            fileInfo = QFileInfo(path)

            if fileInfo.isFile():
                file = QFile(path)

                if file.open(QIODevice.ReadOnly):
                    size = file.size()

                    if size and size < maxFileSize:
                        logUser.info('Importing file: {0}'.format(path))
                        entry = await ipfsop.addPath(path)
                        if entry:
                            self.tracker.clipboardProcess(entry['Hash'])

                    file.close()
            if fileInfo.isDir():
                # Don't check for directory size
                async def entryAdded(entry):
                    logUser.info('{path}: imported'.format(
                        path=entry.get('Name')))

                entry = await ipfsop.addPath(path, callback=entryAdded)
                if entry:
                    self.tracker.clipboardProcess(entry['Hash'])
        except Exception:
            pass

    def onQrEncodeStackPublic(self):
        if len(self.tracker.items) == 0:
            return messageBox('Clipboard stack is empty')

        ensure(self.encodeClipboardItems(encrypt=False))

    def onQrEncodeStackEncrypted(self):
        if len(self.tracker.items) == 0:
            return messageBox('Clipboard stack is empty')

        ensure(self.encodeClipboardItems(encrypt=True))

    @ipfsOp
    async def encodeClipboardItems(self, ipfsop, encrypt=False):
        logUser.info('QR: encoding clipboard stack (encrypted: {enc})'.format(
            enc=encrypt))

        encoder = IPFSQrEncoder()

        for item in self.tracker.items:
            if item.ipfsPath.valid:
                logUser.info('QR: adding item: {item}'.format(
                    item=str(item.ipfsPath)))
                encoder.add(str(item.ipfsPath))

        logUser.info('QR: encoding ..')

        qrName = 'ipfsqr.{}.png'.format(int(time.time()))
        imgPath = self.app.tempDir.filePath(qrName)

        try:
            image = await encoder.encodeAll(loop=self.app.loop,
                                            executor=self.app.executor)
            image.save(imgPath)
        except:
            # :-/
            logUser.info('QR: encoding error ..')
            return
        else:
            logUser.info('QR: encoding successfull!')

        if ipfsop.ctx.currentProfile:
            ipfsop.ctx.currentProfile.qrImageEncoded.emit(encrypt, imgPath)


class ClipboardItemButton(PopupToolButton):
    """
    Represents a ClipboardItem in the clipboard stack
    """

    def __init__(self, rscOpener, clipItem=None, parent=None):
        super().__init__(mode=QToolButton.InstantPopup, parent=parent)

        self._item = None
        self.app = QApplication.instance()
        self.setObjectName('currentClipItem')
        self.setIcon(getMimeIcon('unknown'))
        self.setIconSize(QSize(32, 32))
        self.setToolTip(iClipboardNoValidAddress())
        self.setEnabled(False)
        self.rscOpener = rscOpener
        self.loadingClip = QMovie(':/share/icons/loading.gif')
        self.loadingClip.finished.connect(
            functools.partial(self.loadingClip.start))
        self.menu.setToolTipsVisible(True)

        if isinstance(clipItem, ClipboardItem):
            self.setClipboardItem(clipItem)

        self.clicked.connect(self.onOpen)

        self.setAsHomeAction = QAction(getIcon('go-home.png'),
                                       iClipItemSetAsHome(), self,
                                       triggered=self.onSetAsHome)

        self.hashmarkAction = QAction(getIcon('hashmarks.png'),
                                      iHashmark(), self,
                                      triggered=self.onHashmark)

        self.openAction = QAction(getIcon('terminal.png'),
                                  iClipItemOpen(), self,
                                  shortcut=QKeySequence('Ctrl+o'),
                                  triggered=self.onOpen)

        self.openWithAppAction = QAction(getIcon('terminal.png'),
                                         iClipItemOpenWithApp(), self,
                                         triggered=self.onOpenWithProgram)

        self.openWithDefaultAction = QAction(
            getIcon('terminal.png'),
            iClipItemOpenWithDefaultApp(),
            self,
            triggered=self.onOpenWithDefaultApp)

        self.exploreHashAction = QAction(
            getIcon('folder-open.png'),
            iClipboardEmpty(), self,
            shortcut=QKeySequence('Ctrl+e'),
            triggered=self.onExplore)

        self.downloadAction = QAction(
            getIcon('download.png'),
            iClipboardEmpty(), self,
            triggered=self.onDownload)

        self.dagViewAction = QAction(
            getIcon('ipld-logo.png'),
            iClipboardEmpty(), self,
            shortcut=QKeySequence('Ctrl+g'),
            triggered=self.onDagView)

        self.ipldExplorerAction = QAction(
            getIcon('ipld-logo.png'),
            iClipboardEmpty(), self,
            shortcut=QKeySequence('Ctrl+i'),
            triggered=self.onIpldExplore)

        self.markupRocksAction = QAction(
            getIcon('ipld-logo.png'),
            iClipboardEmpty(), self,
            triggered=self.onMarkdownEdit)

        self.pinAction = QAction(
            getIcon('pin.png'),
            iClipboardEmpty(), self,
            shortcut=QKeySequence('Ctrl+p'),
            triggered=self.onPin)

    @property
    def item(self):
        return self._item

    def setClipboardItem(self, item):
        self.setEnabled(True)
        self._item = item

        self.setToolTip(item.path)

        if item.mimeIcon:
            # Already set icon from mimetype
            self.setIcon(item.mimeIcon)
            ensure(self.updateButton())
        else:
            # MIME type undetected yet (fresh item)
            disconnectSig(self.loadingClip.frameChanged, self.onLoadingFrame)
            self.loadingClip.frameChanged.connect(self.onLoadingFrame)
            self.loadingClip.start()
            item.mimeTypeDetected.connect(self.mimeDetected)

    def onLoadingFrame(self, num):
        self.setIcon(QIcon(self.loadingClip.currentPixmap()))

    def onHashmark(self):
        if self.item:
            addHashmark(self.app.marksLocal, self.item.fullPath,
                        self.item.basename)

    def onSetAsHome(self):
        self.app.settingsMgr.setSetting(CFG_SECTION_BROWSER, CFG_KEY_HOMEURL,
                                        'dweb:{}'.format(self.item.fullPath))

    def onOpenWithProgram(self):
        def onAccept(dlg):
            prgValue = dlg.textValue()
            if len(prgValue) in range(1, 512):
                ensure(self.rscOpener.openWithExternal(
                    self.item.cid, prgValue))

        runDialog(ChooseProgramDialog, accepted=onAccept)

    def onOpenWithDefaultApp(self):
        if self.item.cid:
            ensure(self.rscOpener.openWithSystemDefault(self.item.cid))

    def mimeDetected(self, mType):
        if self.loadingClip.state() == QMovie.Running:
            self.loadingClip.stop()
        ensure(self.updateButton())

    def tooltipMessage(self):
        statInfo = StatInfo(self.item.stat)
        message = '{path} (type: {mimetype})'.format(
            path=self.item.fullPath,
            mimetype=str(self.item.mimeType) if self.item.mimeType else
            iUnknown()
        )
        if statInfo.valid:
            if self.item.mimeType and self.item.mimeType.isDir:
                message += '\n\nTotal size: {total}, links: {links}'.format(
                    total=sizeFormat(statInfo.totalSize),
                    links=statInfo.numLinks
                )
            else:
                message += '\n\nTotal size: {total}'.format(
                    total=sizeFormat(statInfo.totalSize)
                )
        else:
            message += '\n\nNo information on object'
        return message

    @ipfsOp
    async def updateButton(self, ipfsop):
        if not isinstance(self.item, ClipboardItem):
            return

        if self.item.path is None:
            log.debug('Empty path')
            return

        shortened = shortPathRepr(self.item.path)

        self.menu.clear()

        action = self.menu.addSection(shortened)
        action.setToolTip(self.item.fullPath)
        self.menu.addSeparator()

        self.menu.addAction(self.openAction)
        self.menu.addAction(self.openWithAppAction)
        self.menu.addAction(self.openWithDefaultAction)
        self.menu.addSeparator()
        self.menu.addAction(self.setAsHomeAction)
        self.menu.addAction(self.hashmarkAction)
        self.menu.addAction(self.downloadAction)
        self.menu.addSeparator()
        self.menu.addAction(self.dagViewAction)
        self.menu.addAction(self.ipldExplorerAction)
        self.menu.addSeparator()
        self.menu.addAction(self.pinAction)

        self.exploreHashAction.setText(iClipItemExplore())
        self.openAction.setText(iClipItemOpen())
        self.dagViewAction.setText(iClipItemDagView())
        self.hashmarkAction.setText(iClipItemHashmark())
        self.downloadAction.setText(iClipItemDownload())
        self.ipldExplorerAction.setText(iClipItemIpldExplorer())
        self.markupRocksAction.setText(iClipItemMarkupRocks())
        self.pinAction.setText(iClipItemPin())

        self.setToolTip(self.tooltipMessage())

        if not self.item.mimeType:
            return self.updateIcon(getMimeIcon('unknown'))

        icon = None
        if self.item.mimeType.isDir or self.item.mimeType == mimeTypeDag:
            # It's a directory. Add the explore action and disable
            # the actions that don't apply to a folder
            self.menu.addAction(self.exploreHashAction)
            self.openWithAppAction.setEnabled(False)
            self.openWithDefaultAction.setEnabled(False)

            # Look for a favicon
            icon = await getFavIconFromDir(ipfsop, self.item.ipfsPath)
            if icon:
                return self.updateIcon(icon)

        elif self.item.mimeType.isText:
            self.menu.addSeparator()
            self.menu.addAction(self.markupRocksAction)

        elif self.item.mimeType.isImage:
            self.updateIcon(getMimeIcon('image/x-generic'))
            ensure(self.analyzeImage())

        mIcon = getIconFromMimeType(self.item.mimeType)

        if mIcon:
            self.updateIcon(mIcon)

    def updateIcon(self, icon):
        self.item.mimeIcon = icon
        self.setIcon(icon)

    @ipfsOp
    async def analyzeImage(self, ipfsop):
        statInfo = StatInfo(self.item.stat)

        if statInfo.valid:
            size = statInfo.dataSize

            if isinstance(size, int):
                # don't scan anything larger than 4Mb
                if statInfo.dataLargerThan(megabytes(4)):
                    log.debug('{path}: Image too large, not scanning')
                    return
        else:
            # Don't trust this one
            log.debug('No object info for image, bailing out')
            return

        try:
            data = await ipfsop.waitFor(
                ipfsop.client.cat(self.item.path), 12
            )

            if data is None:
                return

            icon = getIconFromImageData(data)
            if icon:
                self.updateIcon(icon)

            # Decode the QR codes in the image if there's any
            qrDecoder = IPFSQrDecoder()
            if not qrDecoder:
                return

            urls = qrDecoder.decode(data)
            if isinstance(urls, list):
                # Display the QR codes in a separate menu
                menu = qrCodesMenuBuilder(urls, self.app.resourceOpener,
                                          parent=self)
                self.menu.addSeparator()
                self.menu.addMenu(menu)

        except aioipfs.APIError:
            pass

    def onOpen(self):
        if self.item:
            ensure(self.rscOpener.open(self.item.ipfsPath, self.item.mimeType))

    def onExplore(self):
        if self.item and self.item.cid:
            self.app.mainWindow.explore(self.item.cid)

    def onDagView(self):
        if self.item:
            view = dag.DAGViewer(self.item.path, self.app.mainWindow)
            self.app.mainWindow.registerTab(
                view, iDagViewer(),
                current=True,
                icon=getIcon('ipld.png'),
                tooltip=self.item.path
            )
        else:
            messageBox(iClipboardEmpty())

    def onIpldExplore(self):
        """
        Open the IPLD explorer application for the current clipboard item
        """
        if self.item:
            mark = self.app.marksLocal.searchByMetadata({
                'title': 'IPLD explorer'})
            if mark:
                link = os.path.join(
                    mark.path, '#', 'explore', stripIpfs(self.item.path))
                self.app.mainWindow.addBrowserTab().browseFsPath(link)

    def onMarkdownEdit(self):
        """
        Open markup.rocks for the current clipboard item
        """
        if self.item:
            mark = self.app.marksLocal.searchByMetadata({
                'title': 'markup.rocks'})
            if mark:
                link = os.path.join(
                    mark.path, '#', self.item.path.lstrip('/'))
                self.app.mainWindow.addBrowserTab().browseFsPath(link)

    def onPin(self):
        if self.item:
            ensure(self.app.ipfsCtx.pin(self.item.path, True, None,
                                        qname='clipboard'))

    def onDownload(self):
        if self.item:
            ensure(self.downloadItem(self.item))

    @ipfsOp
    async def downloadItem(self, ipfsop, item):
        toolbarMain = self.app.mainWindow.toolbarMain
        button = DownloadProgressButton(item.path, item.stat,
                                        parent=self)
        button.show()

        action = toolbarMain.insertWidget(
            toolbarMain.actionStatuses, button)

        button.task = self.app.ipfsTaskOp(self.downloadItemTask,
                                          item, button, action)
        button.cancelled.connect(lambda: toolbarMain.removeAction(action))
        button.downloadFinished.connect(
            lambda: toolbarMain.removeAction(action))

    async def downloadItemTask(self, ipfsop, item, progButton, action):
        downloadsDir = self.app.settingsMgr.downloadsDir

        async def progress(path, read, progButton):
            progButton.downloadProgress.emit(read)

        try:
            await ipfsop.client.get(
                item.path, dstdir=downloadsDir,
                progress_callback=progress,
                progress_callback_arg=progButton)
        except aioipfs.APIError:
            pass
        else:
            progButton.downloadFinished.emit()


class ClipboardItemsStack(QStackedWidget):
    """
    Stacked widget responsible for displaying tool buttons for every
    clipboard item
    """

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

        self.app = QApplication.instance()
        self.app.clipTracker.itemRemoved.connect(self.onItemRemoved)
        self.setObjectName('currentClipItem')
        self.rscOpener = self.app.resourceOpener
        self.setFixedSize(40, 32)
        self.addItemButton()

    def onItemRemoved(self, item):
        for idx in range(0, self.count() + 1):
            button = self.widget(idx)
            if button and button.item == item:
                self.removeWidget(button)

    def findButtonByClipItem(self, item):
        for idx in range(1, self.count() + 1):
            button = self.widget(idx)
            if button and button.item == item:
                return button

    def addItemButton(self, item=None):
        """
        Add a button for a clipboard item on the stack and return it
        """
        button = ClipboardItemButton(
            self.rscOpener,
            clipItem=item,
            parent=self
        )
        self.addWidget(button)
        return button

    def activateItem(self, item):
        """
        Create a tool button for a clipboard item if not registered yet,
        or set it as the current widget of the stack otherwise
        """
        btn = self.findButtonByClipItem(item)
        if not btn:
            button = self.addItemButton(item=item)
            self.setCurrentWidget(button)
        else:
            if btn.item and not btn.item.valid:
                # Rescan the item
                ensure(self.app.clipTracker.scanItem(btn.item))
            self.setCurrentWidget(btn)

    def popupStackItem(self, itemNo):
        itemIdx = self.count() - itemNo

        if itemIdx > 0:
            button = self.widget(itemIdx)
            if button:
                self.setCurrentWidget(button)
                return button

    def getStackItem(self, itemNo):
        itemIdx = self.count() - itemNo

        if itemIdx > 0:
            return self.widget(itemIdx)
