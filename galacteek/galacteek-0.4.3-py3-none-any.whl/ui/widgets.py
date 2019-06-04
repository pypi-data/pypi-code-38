import re
import asyncio

from PyQt5.QtWidgets import QFrame
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QToolButton
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QMenu
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidgetAction
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QListView

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QPoint
from PyQt5.QtCore import QUrl
from PyQt5.QtCore import QMimeData
from PyQt5.QtCore import QSize
from PyQt5.QtCore import QFile
from PyQt5.QtCore import QIODevice
from PyQt5.QtCore import QVariant

from PyQt5.QtGui import QImage
from PyQt5.QtGui import QPixmap

from galacteek.ipfs.stat import StatInfo
from galacteek.ipfs.wrappers import ipfsOp
from galacteek.ipfs.cidhelpers import IPFSPath
from galacteek import ensure

from .helpers import getIcon
from .helpers import getIconFromIpfs
from .helpers import disconnectSig
from .helpers import sizeFormat
from .i18n import iNoTitle
from .i18n import iCancel
from .i18n import iUnknown
from .i18n import iHashmarksLibraryCountAvailable
from .i18n import iLocalHashmarksCount


class GalacteekTab(QWidget):
    def __init__(self, gWindow, **kw):
        super(GalacteekTab, self).__init__(gWindow)
        self.vLayout = QVBoxLayout(self)
        self.setLayout(self.vLayout)

        self.gWindow = gWindow
        self.setAttribute(Qt.WA_DeleteOnClose)

    def tabIndex(self, w=None):
        return self.gWindow.ui.tabWidget.indexOf(w if w else self)

    def setTabName(self, name, widget=None):
        idx = self.tabIndex(w=widget)
        if idx >= 0:
            self.gWindow.ui.tabWidget.setTabText(idx, name)

    def addToLayout(self, widget):
        self.vLayout.addWidget(widget)

    def onClose(self):
        return True

    @ipfsOp
    async def initialize(self, op):
        pass

    @property
    def app(self):
        return self.gWindow.app

    @property
    def loop(self):
        return self.app.loop

    @property
    def profile(self):
        return self.app.ipfsCtx.currentProfile


class HorizontalLine(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)
        self.setStyleSheet('''
            QFrame {
                background-color: #4a9ea1;
            }
        ''')


class URLDragAndDropProcessor:
    fileDropped = pyqtSignal(QUrl)
    ipfsObjectDropped = pyqtSignal(IPFSPath)

    def dragEnterEvent(self, event):
        mimeData = event.mimeData()

        if mimeData.hasUrls() or mimeData.hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        mimeData = event.mimeData()

        if mimeData is None:
            return

        if mimeData.hasUrls():
            for url in mimeData.urls():
                if not url.isValid():
                    continue

                if url.scheme() == 'file' and url.isValid():
                    self.fileDropped.emit(url)
                else:
                    path = IPFSPath(url.toString())
                    if path.valid:
                        self.ipfsObjectDropped.emit(path)
        elif mimeData.hasText():
            text = mimeData.text()
            path = IPFSPath(text)

            if path.valid:
                self.ipfsObjectDropped.emit(path)

        event.acceptProposedAction()


class CheckableToolButton(QToolButton):
    def __init__(self, toggled=None, icon=None, parent=None):
        super(CheckableToolButton, self).__init__(parent)
        self.setCheckable(True)
        self.setAutoRaise(True)

        if toggled:
            self.toggled.connect(toggled)

        if icon:
            self.setIcon(icon)


class IPFSPathClipboardButton(QToolButton):
    def __init__(self, ipfsPath, parent=None):
        super(IPFSPathClipboardButton, self).__init__(parent)

        self.setEnabled(False)
        self.setIcon(getIcon('clipboard.png'))
        self.app = QApplication.instance()
        self.path = ipfsPath
        self.clicked.connect(self.onClicked)

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path):
        if isinstance(path, IPFSPath) and path.valid:
            self.setEnabled(True)
            self.setToolTip('Copy to clipboard: {}'.format(str(path)))
            self._path = path

    def onClicked(self):
        if isinstance(self.path, IPFSPath) and self.path.valid:
            self.app.setClipboardText(str(self.path))


class IPFSUrlLabel(QLabel):
    def __init__(self, ipfsPath, invalidPathLabel='Invalid path', parent=None):
        super(IPFSUrlLabel, self).__init__(parent)

        self.invalidPathMessage = invalidPathLabel
        self.path = ipfsPath
        self.setTextInteractionFlags(Qt.TextSelectableByMouse)

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, val):
        self._path = val

        if self.path and self.path.valid:
            self.url = QUrl('dweb:' + str(self.path))
            self.setText('<a href="{url}">{url}</a>'.format(
                url=self.url.toString()))
        else:
            self.url = None
            self.setText(self.invalidPathMessage)

    def dragEnterEvent(self, event):
        mimeData = event.mimeData()

        if mimeData.hasUrls() or mimeData.hasText():
            event.acceptProposedAction()

    def mimeData(self, indexes):
        mimedata = QMimeData()
        mimedata.setUrls([self.url])
        return mimedata


class PopupToolButton(QToolButton, URLDragAndDropProcessor):
    def __init__(self, icon=None, parent=None, menu=None,
                 mode=QToolButton.MenuButtonPopup, acceptDrops=False):
        super(PopupToolButton, self).__init__(parent)

        self.menu = menu if menu else QMenu()
        self.setPopupMode(mode)
        self.setMenu(self.menu)
        self.setAcceptDrops(acceptDrops)

        if icon:
            self.setIcon(icon)


class IPFSObjectToolButton(QToolButton):
    """
    Used in the quickaccess toolbar
    """
    deleteRequest = pyqtSignal()

    def __init__(self, ipfsPath, icon=None, parent=None):
        super(IPFSObjectToolButton, self).__init__(parent=parent)
        if icon:
            self.setIcon(icon)

    def mousePressEvent(self, event):
        button = event.button()

        if button == Qt.RightButton:
            menu = QMenu()
            menu.addAction('Remove', lambda: self.deleteRequest.emit())
            menu.exec(self.mapToGlobal(event.pos()))

        super().mousePressEvent(event)


class HashmarkToolButton(QToolButton):
    """
    Used in the quickaccess toolbar
    """
    deleteRequest = pyqtSignal()

    def __init__(self, mark, icon=None, parent=None):
        super(HashmarkToolButton, self).__init__(icon=icon,
                                                 parent=parent)
        if icon:
            self.setIcon(icon)

        self._hashmark = mark

    @property
    def hashmark(self):
        return self._hashmark

    def mousePressEvent(self, event):
        button = event.button()

        if button == Qt.RightButton:
            menu = QMenu()
            menu.addAction('Remove', lambda: self.deleteRequest.emit())
            menu.exec(self.mapToGlobal(event.pos()))

        super().mousePressEvent(event)


class _HashmarksCommon:
    def makeAction(self, path, mark):
        tLenMax = 64
        title = mark['metadata'].get('title', iNoTitle())
        icon = mark.get('icon', None)
        fullTitle = title

        if len(title) > tLenMax:
            title = '{0} ...'.format(title[0:tLenMax])

        action = QAction(title, self)
        action.setToolTip(fullTitle)
        action.setData({
            'path': path,
            'mark': mark,
            'iconcid': icon
        })

        if not icon:
            # Default icon
            action.setIcon(getIcon('ipfs-logo-128-white-outline.png'))

        return action

    @ipfsOp
    async def loadMarkIcon(self, ipfsop, action, iconCid):
        icon = await getIconFromIpfs(ipfsop, iconCid)
        if icon:
            await ipfsop.sleep()

            action.setIcon(icon)
            data = action.data()
            data['iconloaded'] = True
            action.setData(data)


class HashmarkMgrButton(PopupToolButton, _HashmarksCommon):
    hashmarkClicked = pyqtSignal(str, str)

    def __init__(self, marks, iconFile='hashmarks.png',
                 maxItemsPerCategory=128, parent=None):
        super(HashmarkMgrButton, self).__init__(parent=parent,
                                                mode=QToolButton.InstantPopup)

        self.setObjectName('hashmarksMgrButton')
        self.menu.setObjectName('hashmarksMgrMenu')
        self.hCount = 0
        self.marks = marks
        self.cMenus = {}
        self.maxItemsPerCategory = maxItemsPerCategory
        self.setIcon(getIcon(iconFile))

        disconnectSig(self.marks.changed, self.onChanged)

        self.marks.changed.connect(self.onChanged)
        self.marks.markAdded.connect(self.onMarkAdded)

    def onMarkAdded(self):
        ensure(self.updateIcons())

    def onChanged(self):
        self.updateMenu()

    async def updateIcons(self):
        for mName, menu in self.cMenus.items():
            await asyncio.sleep(0)

            for action in menu.actions():
                data = action.data()

                if 'iconloaded' not in data and data['iconcid']:
                    ensure(self.loadMarkIcon(action, data['iconcid']))

    def updateMenu(self):
        self.hCount = 0
        categories = self.marks.getCategories()

        for category in categories:
            marks = self.marks.getCategoryMarks(category)
            mItems = marks.items()

            if len(mItems) not in range(1, self.maxItemsPerCategory):
                continue

            if category not in self.cMenus:
                self.cMenus[category] = QMenu(category)
                self.cMenus[category].triggered.connect(self.linkActivated)
                self.cMenus[category].setObjectName('hashmarksMgrMenu')
                self.menu.addMenu(self.cMenus[category])

            menu = self.cMenus[category]
            menu.setIcon(getIcon('stroke-cube.png'))

            def exists(path):
                for action in menu.actions():
                    if action.data()['path'] == path:
                        return action

            if len(mItems) in range(1, self.maxItemsPerCategory):
                for path, mark in mItems:
                    self.hCount += 1

                    if exists(path):
                        continue

                    menu.addAction(self.makeAction(path, mark))
            else:
                menu.hide()

        self.setToolTip(iLocalHashmarksCount(self.hCount))

    def linkActivated(self, action):
        data = action.data()
        path, mark = data['path'], data['mark']

        if mark:
            if 'metadata' not in mark:
                return
            self.hashmarkClicked.emit(
                path,
                mark['metadata']['title']
            )


class HashmarksLibraryButton(PopupToolButton, _HashmarksCommon):
    hashmarkClicked = pyqtSignal(str, str)

    def __init__(self, iconFile='hashmarks-library.png',
                 maxItemsPerCategory=128, parent=None):
        super(HashmarksLibraryButton, self).__init__(
            parent=parent, mode=QToolButton.InstantPopup)

        self.cMenus = {}
        self.hCount = 0
        self.maxItemsPerCategory = maxItemsPerCategory
        self.setIcon(getIcon(iconFile))
        self.setObjectName('hashmarksLibraryButton')
        self.menu.setObjectName('hashmarksLibraryMenu')
        self.searchMenu = None
        self.addSearchMenu()

    def addSearchMenu(self):
        if self.searchMenu is not None:
            return

        self.searchMenu = QMenu('Search')
        self.menu.addMenu(self.searchMenu)

        self.searchLine = QLineEdit()
        self.searchLine.returnPressed.connect(self.onSearch)
        self.searchWAction = QWidgetAction(self)
        self.searchWAction.setDefaultWidget(self.searchLine)
        self.searchMenu.addAction(self.searchWAction)
        self.searchMenu.setEnabled(False)

    def onSearch(self):
        pos = self.searchLine.mapToGlobal(QPoint(0, 0))
        text = self.searchLine.text()

        resultsMenu = QMenu()
        resultsMenu.triggered.connect(
            lambda action: self.linkActivated(
                action, closeMenu=True))
        self.searchTextInMenu(self.menu, text, resultsMenu)
        resultsMenu.exec(pos)

    def searchTextInMenu(self, menu, text, rMenu):
        for action in menu.actions():
            menu = action.menu()
            if menu:
                self.searchTextInMenu(menu, text, rMenu)
            else:
                data = action.data()
                if not isinstance(data, dict):
                    continue

                path = data['path']
                mark = data['mark']

                maTitle = re.search(text, mark['metadata']['title'],
                                    re.IGNORECASE)
                maDesc = re.search(text, mark['metadata']['description'],
                                   re.IGNORECASE)
                if maTitle or maDesc:
                    rMenu.addAction(self.makeAction(path, mark))

    def updateMenu(self, ipfsMarks):
        categories = ipfsMarks.getCategories()

        for category in categories:
            marks = ipfsMarks.getCategoryMarks(category)
            mItems = marks.items()

            if len(mItems) not in range(1, self.maxItemsPerCategory):
                continue

            if category not in self.cMenus:
                self.cMenus[category] = QMenu(category)
                self.cMenus[category].triggered.connect(self.linkActivated)
                self.cMenus[category].setObjectName('hashmarksLibraryMenu')
                self.menu.addMenu(self.cMenus[category])

            menu = self.cMenus[category]

            menu.setIcon(getIcon('stroke-cube.png'))

            def exists(path):
                for action in menu.actions():
                    if action.data()['path'] == path:
                        return action

            for path, mark in mItems:
                if exists(path):
                    continue

                action = self.makeAction(path, mark)
                menu.addAction(action)
                self.hCount += 1

        self.setToolTip(iHashmarksLibraryCountAvailable(self.hCount))
        if self.hCount > 0:
            self.searchMenu.setEnabled(True)

    def linkActivated(self, action, closeMenu=False):
        data = action.data()
        path, mark = data['path'], data['mark']

        if mark:
            if 'metadata' not in mark:
                return

            self.hashmarkClicked.emit(
                path,
                mark['metadata']['title']
            )

            if closeMenu:
                self.menu.hide()


class ImageWidget(QLabel):
    """
    Displays an image stored in IPFS into a QLabel
    """

    def __init__(self, scaleWidth=64, parent=None):
        super(ImageWidget, self).__init__(parent)

        self._imgPath = None
        self._scaleWidth = scaleWidth

    @property
    def imgPath(self):
        return self._imgPath

    @ipfsOp
    async def load(self, ipfsop, path):
        try:
            imgData = await ipfsop.waitFor(
                ipfsop.client.cat(path), 8
            )

            if not imgData:
                raise Exception('Failed to load image')

            img1 = QImage()
            img1.loadFromData(imgData)
            img = img1.scaledToWidth(self._scaleWidth)

            self.setPixmap(QPixmap.fromImage(img))
            self._imgPath = path
            return True
        except Exception:
            return False


class DownloadProgressButton(PopupToolButton):
    downloadProgress = pyqtSignal(int)
    downloadFinished = pyqtSignal()
    cancelled = pyqtSignal()

    def __init__(self, path, stat, parent=None):
        super(DownloadProgressButton, self).__init__(
            icon=getIcon('download.png'),
            parent=parent, mode=QToolButton.InstantPopup)
        self.downloadProgress.connect(self.onProgress)
        self.downloadFinished.connect(self.onFinished)
        self.path = path
        self.stat = stat
        self.readBytes = 0
        self.task = None

        self.menu.addAction(iCancel(), self.onCancel)

    def onCancel(self):
        if self.task:
            try:
                self.task.cancel()
            except:
                pass

            self.cancelled.emit()

    def onProgress(self, read):
        statInfo = StatInfo(self.stat)

        self.readBytes = read
        size = sizeFormat(statInfo.totalSize) if statInfo.valid else \
            iUnknown()

        self.setToolTip('{path} (size: {size}): downloaded {dl}'.format(
            path=self.path,
            size=size,
            dl=sizeFormat(self.readBytes))
        )

    def onFinished(self):
        self.setToolTip('{path}: download finished'.format(path=self.path))


class IconSelector(QComboBox):
    """
    A simple icon selector. The selected icon is injected in the
    repository and a signal with its CID is emitted
    """
    iconSelected = pyqtSignal(str)
    emptyIconSelected = pyqtSignal()

    iconsList = [
        ':/share/icons/distributed.png',
        ':/share/icons/atom.png',
        ':/share/icons/atom-rpg.png',
        ':/share/icons/cerebro.png',
        ':/share/icons/ipfs-cube-64.png',
        ':/share/icons/ipfs-logo-128-white.png',
        ':/share/icons/code-fork.png',
        ':/share/icons/cube-nova-aqua.png',
        ':/share/icons/cube-nova-orange.png',
        ':/share/icons/cubehouse.png',
        ':/share/icons/fragments.png',
        ':/share/icons/go-home.png',
        ':/share/icons/hotspot.png',
        ':/share/icons/ipld-logo.png',
        ':/share/icons/pyramid-aqua.png',
        ':/share/icons/pyramid-stack.png',
        ':/share/icons/multimedia.png',
        ':/share/icons/folder-documents.png',
        ':/share/icons/folder-pictures.png',
        ':/share/icons/orbitdb.png',
        ':/share/icons/pyramid-hierarchy.png',
        ':/share/icons/sweethome.png',
        ':/share/icons/stroke-code.png',
        ':/share/icons/web-devel.png',
        ':/share/icons/mimetypes/image-x-generic.png',
        ':/share/icons/mimetypes/application-pdf.png',
        ':/share/icons/mimetypes/application-epub+zip.png',
        ':/share/icons/mimetypes/application-x-directory.png',
        ':/share/icons/mimetypes/text-html.png'
    ]

    def __init__(self, parent=None, offline=False, allowEmpty=False):
        super(IconSelector, self).__init__(parent)

        self.app = QApplication.instance()
        self.allowEmpty = allowEmpty
        self.offline = offline
        self.iconCid = None

        if self.app.system == 'Linux':
            self.setIconSize(QSize(64, 64))

        if allowEmpty is True:
            self.addItem('No icon')

        for iconP in self.iconsList:
            icon = getIcon(iconP)
            if icon:
                self.addItem(icon, '', QVariant(iconP))

        self.view = QListView(self)
        self.setView(self.view)
        self.currentIndexChanged.connect(self.onIndexChanged)

        if allowEmpty is False:
            self.injectCurrent()

    def injectCurrent(self):
        self.injectIconFromIndex(self.currentIndex())

    def injectIconFromIndex(self, idx):
        iconPath = self.itemData(idx)
        if iconPath:
            ensure(self.injectQrcIcon(iconPath))

    def onIndexChanged(self, idx):
        if self.allowEmpty and idx == 0:
            self.emptyIconSelected.emit()
        else:
            self.injectIconFromIndex(idx)

    @ipfsOp
    async def injectQrcIcon(self, op, iconPath):
        _file = QFile(iconPath)
        if _file.exists():
            if not _file.open(QIODevice.ReadOnly):
                return False

            data = _file.readAll().data()

            entry = await op.client.add_bytes(data, offline=self.offline)
            if entry:
                self.iconCid = entry['Hash']
                self.iconSelected.emit(self.iconCid)
                self.setToolTip(self.iconCid)
                return True
