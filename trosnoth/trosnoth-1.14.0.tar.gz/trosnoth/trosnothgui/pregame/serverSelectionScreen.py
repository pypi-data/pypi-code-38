import logging

from twisted.internet.protocol import ClientCreator
from twisted.internet import reactor, defer
from twisted.protocols import amp

from trosnoth.const import JOIN_AUTH_LAN_GAME, JOIN_LAN_GAME
from trosnoth.gui.framework import framework, table, elements, scrollableCanvas
from trosnoth.gui.framework.prompt import intValidator, PasswordBox
from trosnoth.gui.framework.elements import TextButton, TextElement
from trosnoth.gui.framework.checkbox import CheckBox
from trosnoth.gui.common import (ScaledScreenAttachedPoint, Location,
        ScaledScalar, ScaledSize, ScaledArea, Area, AttachedPoint, Size, Region,
        ScaledPoint)
from trosnoth.gui.framework.tabContainer import TabContainer, TabSize
from trosnoth.gui.framework.tab import Tab
from trosnoth.gui.framework.dialogbox import OkBox
from trosnoth.network import authcommands
from trosnoth.network.lobby import authenticate, encryptPassword
from trosnoth.trosnothgui.common import button
from trosnoth.trosnothgui.pregame.authServerLoginBox import PasswordGUI
from trosnoth.trosnothgui.pregame.playscreen import PlayAuthScreen

log = logging.getLogger(__name__)

HOSTNAME_COLUMN = 0
PORT_COLUMN = 1
CONNECT_COLUMN = 2
ACCOUNT_COLUMN = 3
MOVE_UP_COLUMN = 4
MOVE_DOWN_COLUMN = 5
DELETE_COLUMN = 6


class AccountSettingsScreen(framework.CompoundElement):
    passwordGUIFactory = PasswordGUI

    def __init__(self, app, host, port, onClose):
        super(AccountSettingsScreen, self).__init__(app)
        self.onClose = onClose
        self.host = host
        self.port = port

        area = ScaledArea(50,140,924, 570)
        alpha = 192 if app.displaySettings.alphaOverlays else 255
        font = app.screenManager.fonts.bigMenuFont
        self.tabContainer = TabContainer(self.app, area, font,
                app.theme.colours.playTabBorder)
        self.background = elements.SolidRect(self.app,
                app.theme.colours.playMenu, alpha, Area(AttachedPoint((0,0),
                self.tabContainer._getTabRect), TabSize(self.tabContainer)))

        self.passwordTab = ChangePasswordTab(app, host, onClose=self.close,
                onSave=self.save)
        self.tabContainer.addTab(self.passwordTab)
        self.passwordGetter = self.passwordGUIFactory(self.app)

        self.elements = [self.background, self.tabContainer]

        self.protocol = None
        d = ClientCreator(reactor, amp.AMP).connectTCP(host, port)
        d.addCallbacks(self.connectionEstablished, self.connectionFailed)

    @defer.inlineCallbacks
    def connectionEstablished(self, protocol):
        self.protocol = protocol
        try:
            yield authenticate(protocol, self.host, self.passwordGetter)
        except:
            OkBox(self.app, ScaledSize(450, 150), 'Trosnoth',
                    'Unable to authenticate with server').show()
            self.close()
            return

        try:
            result = yield self.protocol.callRemote(
                    authcommands.GetSupportedSettings)
            tabs = set(result['result'])
            self.showTabs(tabs)
        except:
            log.error('Error calling GetSupportedSettings', exc_info=True)
            OkBox(self.app, ScaledSize(450, 150), 'Trosnoth',
                    'Error communicating with server').show()
            self.close()
            return

    def showTabs(self, tabs):
        tabs = set(tabs)

    def connectionFailed(self, reason):
        box = OkBox(self.app, ScaledSize(450, 150), 'Trosnoth',
                'Could not connect to server')
        box.show()
        self.close()

    def close(self):
        if self.protocol and self.protocol.transport.connected:
            self.protocol.transport.loseConnection()
        self.onClose()

    @defer.inlineCallbacks
    def save(self):
        try:
            failReason = yield self.passwordTab.save(self.protocol)
        except:
            log.error('Error saving account settings', exc_info=True)
            failReason = 'Error saving settings to server'

        if failReason:
            OkBox(self.app, ScaledSize(450, 150), 'Trosnoth', failReason).show()
        else:
            self.close()


class ServerSelectionScreen(framework.CompoundElement):
    connectScreenFactory = PlayAuthScreen
    accountScreenFactory = AccountSettingsScreen

    def __init__(self, app, onClose):
        super(ServerSelectionScreen, self).__init__(app)
        self.onClose = onClose

        area = ScaledArea(50,140,924, 570)
        if app.displaySettings.alphaOverlays:
            alpha = 192
        else:
            alpha = 255
        font = app.screenManager.fonts.bigMenuFont
        self.tabContainer = TabContainer(self.app, area, font,
                app.theme.colours.playTabBorder)
        self.background = elements.SolidRect(self.app,
                app.theme.colours.playMenu, alpha, Area(AttachedPoint((0,0),
                self.tabContainer._getTabRect), TabSize(self.tabContainer)))

        self.tab = ServerSelectionTab(app, onClose=onClose, onJoin=self.join,
                onAccountSettings=self.accountSettings)
        self.tabContainer.addTab(self.tab)

        self.setElements()

    def join(self, servers):
        playAuthScreen = self.connectScreenFactory(self.app,
                onSucceed=self.onClose, onFail=self.joinFailed)
        self.elements = [playAuthScreen]
        playAuthScreen.begin(servers, canHost=False)

    def joinFailed(self):
        self.setElements()

    def reload(self):
        self.tab.reload()
        self.setElements()

    def setElements(self):
        self.elements = [self.background, self.tabContainer]

    def accountSettings(self, host, port):
        accountScreen = self.accountScreenFactory(self.app, host, port,
                onClose=self.reload)
        self.elements = [accountScreen]

class ServerSelectionTab(Tab, framework.CompoundElement):
    def __init__(self, app, onClose, onJoin, onAccountSettings):
        super(ServerSelectionTab, self).__init__(app, 'Server Settings')
        self.onClose = onClose
        self.onJoin = onJoin
        self.onAccountSettings = onAccountSettings
        self.setupButtons()

    def setupButtons(self):
        lanButtonPos = Location(ScaledScreenAttachedPoint(ScaledPoint(100, 550),
                'topleft'))
        self.lanButton = CheckBox(self.app, lanButtonPos, 'LAN Discovery',
                self.app.screenManager.fonts.serverSelectionCheckboxesFont,
                self.app.theme.colours.mainMenuColour,
                initValue=self.app.connectionSettings.lanGames, style='circle',
                fillColour=self.app.theme.colours.mainMenuColour)
        self.lanButton.onValueChanged.addListener(lambda sender: self.save())

        lanSearchButtonPos = Location(ScaledScreenAttachedPoint(
                ScaledPoint(380, 550), 'topleft'))
        self.lanSearchButton = TextButton(self.app, lanSearchButtonPos,
                'Search LAN for Game',
                self.app.screenManager.fonts.serverSelectionCheckboxesFont,
                self.app.theme.colours.mainMenuHighlight,
                self.app.theme.colours.white,
                onClick=lambda sender:self.joinLan())

        newButtonPos = Location(ScaledScreenAttachedPoint(
                ScaledPoint(850, 285), 'topleft'))
        self.newButton = TextButton(self.app, newButtonPos, '+ Server',
                self.app.screenManager.fonts.serverSelectionCheckboxesFont,
                self.app.theme.colours.serverSelectionNewItem,
                self.app.theme.colours.white,
                onClick=lambda sender:self.newServer())

        self.closeButton = elements.TextButton(self.app,
            Location(ScaledScreenAttachedPoint(
                    ScaledSize(-70, 650), 'topright'), 'topright'),
            'done',
            self.app.screenManager.fonts.bigMenuFont,
            self.app.theme.colours.mainMenuHighlight,
            self.app.theme.colours.white,
            onClick=lambda sender:self.onClose(),
        )

    def setupTable(self):
        position = Location(ScaledScreenAttachedPoint(
                ScaledPoint(100, 200), 'topleft'), 'topleft')
        # position is merely temporary
        self.serverTable = table.Table(self.app, position)
        hostColumn = table.TextBoxColumn(self.app, self.serverTable,
                ScaledScalar(290))
        portColumn = table.TextBoxColumn(self.app, self.serverTable,
                ScaledScalar(70))
        connectButtonColumn = table.TextButtonColumn(self.app, self.serverTable,
                ScaledScalar(80))
        accountButtonColumn = table.TextButtonColumn(self.app, self.serverTable,
                ScaledScalar(100))
        upButtonColumn = table.TextButtonColumn(self.app, self.serverTable,
                ScaledScalar(40))
        downButtonColumn = table.TextButtonColumn(self.app, self.serverTable,
                ScaledScalar(40))
        deleteButtonColumn = table.TextButtonColumn(self.app, self.serverTable,
                ScaledScalar(40))

        self.serverTable.addColumns([
            hostColumn,
            portColumn,
            connectButtonColumn,
            accountButtonColumn,
            upButtonColumn,
            downButtonColumn,
            deleteButtonColumn,
        ])

        self.serverTable.setBorderWidth(4)
        self.serverTable.setBorderColour((0, 0, 0))

        with self.serverTable.style as s:
            s.backColour = (255, 255, 255)
            s.foreColour = self.app.theme.colours.mainMenuColour
            s.font = self.app.screenManager.fonts.smallMenuFont
            s.padding = (4, 1)
            s.hasShadow = True
            s.shadowColour = (0, 0, 0)

        hostColumn.style.textAlign = 'midright'
        portColumn.style.textAlign = 'center'

        for column in (connectButtonColumn, accountButtonColumn, upButtonColumn,
                downButtonColumn):
            with column.style as s:
                s.textAlign = 'center'
                s.foreColour = self.app.theme.colours.mainMenuHighlight
                s.hoverColour = self.app.theme.colours.black

        with deleteButtonColumn.style as s:
            s.foreColour = self.app.theme.colours.red
            s.backColour = self.app.theme.colours.black
            s.hoverColour = self.app.theme.colours.white
            s.textAlign = 'center'

        self.serverTable.setDefaultHeight(ScaledScalar(40))

        # Title row
        row = self.serverTable.addRow()
        row[HOSTNAME_COLUMN].setText('Host Name')
        row[HOSTNAME_COLUMN].style.foreColour = self.app.theme.colours.black
        row[HOSTNAME_COLUMN].setReadOnly(True)
        row[PORT_COLUMN].setText('Port')
        row[PORT_COLUMN].style.foreColour = self.app.theme.colours.black
        row[PORT_COLUMN].setReadOnly(True)

        self.serverTable.getRow(0).style.backColour = (
                self.app.theme.colours.grey)

    def setupCanvas(self):
        position = Location(ScaledScreenAttachedPoint(
                ScaledPoint(100, 200), 'topleft'), 'topleft')
        maxSize = 325 * self.app.screenManager.scaleFactor
        size = self.serverTable._getSize()
        if size[1] > maxSize:
            # We will be using the scrollbars
            displaySize = (size[0] + scrollableCanvas.ScrollBar.defaultWidth,
                    maxSize)
        else:
            displaySize = size
        self.canvas = scrollableCanvas.ScrollableCanvas(self.app, position,
                Size(*size), Size(*displaySize))
        self.serverTable.pos = Location(
                scrollableCanvas.ScrollableCanvasAttachedPoint(self.canvas,
                (0,0)), 'topleft')
        self.canvas.elements.append(self.serverTable)


    def addRow(self, host, port, httpAddress):
        index = len(self.httpAddresses) # 0-based index into list of servers
        row = self.serverTable.addRow()
        row[HOSTNAME_COLUMN].setText(host)
        row[HOSTNAME_COLUMN].onValueChanged.addListener(self.hostnameChanged)
        row[PORT_COLUMN].setText(str(port))
        row[PORT_COLUMN].setValidator(lambda text:(intValidator(text) and
                int(text) < 65536))
        row[PORT_COLUMN].setMaxLength(5)
        row[PORT_COLUMN].onValueChanged.addListener(self.portChanged)
        onClickConnect = lambda sender: self.join(index)
        onClickDelete = lambda sender: self.delete(index)
        row[CONNECT_COLUMN].setText('play')
        row[CONNECT_COLUMN].setOnClick(onClickConnect)

        onClickAccount = lambda sender: self.showAccountScreen(index)
        row[ACCOUNT_COLUMN].setText('account')
        row[ACCOUNT_COLUMN].setOnClick(onClickAccount)

        if index > 0:
            onClickUp = lambda sender: self.moveUp(index)
            row[MOVE_UP_COLUMN].setText('^')
            row[MOVE_UP_COLUMN].setOnClick(onClickUp)

            onClickDown = lambda sender: self.moveDown(index-1)
            self.serverTable.getRow(index)[MOVE_DOWN_COLUMN].setText('V')
            self.serverTable.getRow(index)[MOVE_DOWN_COLUMN].setOnClick(
                    onClickDown)
        else:
            row[MOVE_UP_COLUMN].setText('-')

        row[MOVE_DOWN_COLUMN].setText('-')
        row[DELETE_COLUMN].setText('X')
        row[DELETE_COLUMN].setOnClick(onClickDelete)
        self.httpAddresses.append(httpAddress)

    def moveUp(self, index):
        servers = list(self.app.connectionSettings.servers)
        temp = servers[index]
        servers[index] = servers[index-1]
        servers[index-1] = temp
        self.app.connectionSettings.servers = tuple(servers)
        self.app.connectionSettings.save()
        self.reload()

    def moveDown(self, index):
        servers = list(self.app.connectionSettings.servers)
        temp = servers[index]
        servers[index] = servers[index+1]
        servers[index+1] = temp
        self.app.connectionSettings.servers = tuple(servers)
        self.app.connectionSettings.save()
        self.reload()

    def delete(self, index):
        servers = list(self.app.connectionSettings.servers)
        del servers[index]
        self.app.connectionSettings.servers = tuple(servers)
        self.app.connectionSettings.save()
        self.reload()

    def newServer(self):
        servers = list(self.app.connectionSettings.servers)
        servers.append(('', 6787, ''))
        self.app.connectionSettings.servers = tuple(servers)
        self.app.connectionSettings.save()
        self.reload()

    def join(self, index):
        row = self.serverTable.getRow(index+1)
        hostname = row[HOSTNAME_COLUMN].getText()
        port = int(row[PORT_COLUMN].getText())
        if port > 65535:
            self.throwPortError()
        else:
            servers = [(hostname, port, '')]
            self.onJoin(tuple(servers))

    def showAccountScreen(self, index):
        row = self.serverTable.getRow(index+1)
        hostname = row[HOSTNAME_COLUMN].getText()
        port = int(row[PORT_COLUMN].getText())
        if port > 65535:
            self.throwPortError()
        else:
            self.onAccountSettings(hostname, port)

    def joinLan(self):
        if self.app.connectionSettings.lanGames:
            self.onJoin((JOIN_AUTH_LAN_GAME, JOIN_LAN_GAME))
        else:
            self.onJoin(())

    def hostnameChanged(self, cell):
        self.httpAddresses[cell.rowNum - 1] = None
        self.save()

    def portChanged(self, cell):
        text = cell.getText()
        if text != '':
            port = int(text)
            if port > 65535:
                self.throwPortError()
                return
        # Else:
        self.save()

    def throwPortError(self):
        box = OkBox(self.app, ScaledSize(450, 150), 'Trosnoth',
                    'Port numbers must be less than 65536')
        box.show()

    def onJoinFailed(self):
        self.setElements()

    def setElements(self):
        self.elements = [self.canvas, self.lanButton, self.lanSearchButton,
                self.newButton, self.closeButton]

    def save(self):
        servers = []
        for rowNum in range(0, len(self.httpAddresses)):
            row = self.serverTable.getRow(rowNum+1)
            hostname = row[HOSTNAME_COLUMN].getText()
            port = int(row[PORT_COLUMN].getText())
            if port < 1 or port > 65535:
                return
            httpAddress = self.httpAddresses[rowNum]
            if httpAddress is None: # Indicates a new or a changed row
                httpAddress = self.getDefaultHttpAddress(hostname, port)
            servers.append((hostname, port, httpAddress))

        self.app.connectionSettings.lanGames = ('afterinet' if
                self.lanButton.getValue() else 'never')
        self.app.connectionSettings.servers = tuple(servers)
        self.app.connectionSettings.save()

    def getDefaultHttpAddress(self, hostname, port):
        if (hostname, port) == ('localhost', 6787):
            return 'http://localhost:8080/'
        else:
            return 'http://%s/' % (hostname,)

    def reload(self):
        self.httpAddresses = []
        self.setupTable()
        for server in self.app.connectionSettings.servers:
            self.addRow(*server)
        self.setupCanvas()
        self.setElements()

class ChangePasswordTab(Tab, framework.TabFriendlyCompoundElement):
    def __init__(self, app, host, onClose, onSave):
        super(ChangePasswordTab, self).__init__(app, 'Password')
        self.onClose = onClose
        self.onSave = onSave
        self.host = host

        font = app.screenManager.fonts.defaultTextBoxFont
        labelColour = app.theme.colours.dialogBoxTextColour
        inputColour = app.theme.colours.white

        label = TextElement(self.app,
            'Use this form to change your password for %s' % (self.host,),
            font=self.app.screenManager.fonts.smallMenuFont,
            pos=Location(ScaledScreenAttachedPoint(
                ScaledPoint(100, 200), 'topleft'), 'topleft'),
            colour=self.app.theme.colours.mainMenuColour,
        )

        self.passwordField = PasswordBox(app,
            Region(topleft=self.Relative(0.1, 0.48),
                bottomright=self.Relative(0.9, 0.64)),
                font=font, colour=inputColour,
                onClick=self.setFocus, onTab=self.tabNext)

        self.passwordField2 = PasswordBox(app,
            Region(topleft=self.Relative(0.1, 0.8),
                bottomright=self.Relative(0.9, 0.96)),
                font=font, colour=inputColour,
                onClick=self.setFocus, onTab=self.tabNext)

        self.elements = [
            label,
            TextElement(app, 'New password', font,
                Location(self.Relative(0.1, 0.43), 'midleft'),
                labelColour),
            self.passwordField,
            TextElement(app, 'Retype new password', font,
                Location(self.Relative(0.1, 0.75), 'midleft'),
                labelColour),
            self.passwordField2,
            button(app, 'save', self.onSave, (-100, -75), 'midbottom',
                    secondColour=app.theme.colours.white),
            button(app, 'cancel', self.cancel, (100, -75), 'midbottom',
                    secondColour=app.theme.colours.white),
        ]

        self.tabOrder = [self.passwordField, self.passwordField2]

    @defer.inlineCallbacks
    def save(self, protocol):
        try:
            if self.passwordField.value != self.passwordField2.value:
                defer.returnValue('Passwords do not match')
                return
            if self.passwordField.value:
                data = yield encryptPassword(protocol, self.passwordField.value)
                yield protocol.callRemote(authcommands.SetPassword,
                        password=data)
        except Exception:   # Must not be naked or returnValue is caught
            log.error('Error storing password', exc_info=True)
            defer.returnValue('Error saving settings')
            return

        defer.returnValue('')
        return

    def cancel(self):
        self.onClose()
