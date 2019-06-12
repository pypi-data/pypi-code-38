import logging

from trosnoth.gui.framework.menu import MenuDisplay
from trosnoth.gui.menu.menu import MenuManager, Menu, MenuItem
from trosnoth.gui.common import Abs, Location, Region, Canvas, ScaledSize, Area
from trosnoth.gui.framework.dialogbox import (
    DialogBox, DialogResult, DialogBoxAttachedPoint,
)
from trosnoth.gui.framework.elements import (
    TextButton, SolidRect, TextElement,
)
from trosnoth.gui.framework.framework import CompoundElement
from trosnoth.gui.framework.prompt import InputBox, intValidator
from trosnoth.messages import (
    PlayerIsReadyMsg, SetPreferredTeamMsg, SetPreferredDurationMsg,
    SetPreferredSizeMsg, SetPreferredLevelMsg,
)
from trosnoth.model.universe_base import NO_PLAYER
from trosnoth.trosnothgui.ingame.dialogs import HeadSelector
from trosnoth.utils.event import Event

log = logging.getLogger(__name__)

MENU_WIDTH = 120


class GameVoteMenu(CompoundElement):
    def __init__(self, app, world, onChange=None):
        CompoundElement.__init__(self, app)
        self.world = world
        self.playerId = NO_PLAYER

        self.readyMenu = ReadyMenu(self, 0)
        self.levelMenu = LevelMenu(self, MENU_WIDTH)
        self.teamMenu = TeamMenu(self, 2 * MENU_WIDTH)
        self.sizeMenu = SizeMenu(self, 3 * MENU_WIDTH)
        self.durationMenu = DurationMenu(self, 4 * MENU_WIDTH)

        self.onChange = Event()
        if onChange is not None:
            self.onChange.addListener(onChange)

        self.subMenu = GameVoteSubMenu(app)
        font = app.screenManager.fonts.ingameMenuFont
        self.elements = [
            SolidRect(app, (0, 64, 192), None,
                Region(topleft=Abs(0,0), width=Abs(4*MENU_WIDTH),
                height=Abs(font.getHeight(app)+2))),
            self.subMenu,
            self.readyMenu.button,
            self.levelMenu.button,
            self.teamMenu.button,
            self.sizeMenu.button,
            self.durationMenu.button,
        ]

    def update(self, player):
        self.playerId = player.id
        self.readyMenu.updateTitle(player)
        self.levelMenu.updateTitle(player)
        self.teamMenu.updateTitle(player)
        self.sizeMenu.updateTitle(player)
        self.durationMenu.updateTitle(player)
        if self.subMenu.manager.menu is not None:
            self.subMenu.manager.menu.update()

    def showSubMenu(self, menu):
        menu.update()
        if self.subMenu.manager.menu is menu or self.subMenu.hidden:
            self.subMenu.hide()
        self.subMenu.manager.setDefaultMenu(menu)
        self.subMenu.location = menu.button.pos

    def hideSubMenu(self):
        if not self.subMenu.hidden:
            self.subMenu.hide()

class GameVoteSubMenu(MenuDisplay):
    ACCELERATION = 1000     # pix/s/s
    def __init__(self, app, keymapping=None):
        font = app.screenManager.fonts.ingameMenuFont
        titleColour = (255, 255, 255)
        stdColour = (255, 255, 0)
        hvrColour = (0, 255, 255)
        backColour = (0, 64, 192)
        disabledColour = (128, 128, 128)
        autosize = True
        hidable = True
        size = Abs(MENU_WIDTH, 10)

        manager = MenuManager()

        location = Location(Abs(0, 0))
        MenuDisplay.__init__(self, app, location, size, font, manager,
                titleColour, stdColour, hvrColour, disabledColour, backColour,
                autosize, hidable, keymapping)

class CountedMenuItem(MenuItem):
    def __init__(self, caption, action=None, listener=None):
        self.caption = caption
        self._count = 0
        MenuItem.__init__(self, caption, action, listener)

    def _getCount(self):
        return self._count
    def _setCount(self, count):
        self._count = count
        self.name = '%s (%d)' % (self.caption, self._count)
    count = property(_getCount, _setCount)

class SelectionMenu(Menu):
    def __init__(self, gvm, pos, items):
        self.gvm = gvm
        self.selected = 0

        Menu.__init__(self, '', items, self.selectItem)

        app = gvm.app
        stdColour = (255, 255, 0)
        hvrColour = (0, 255, 255)
        backColour = (0, 64, 192)
        self.button = TextButton(app, Location(Abs(pos, 0)), '',
            app.screenManager.fonts.ingameMenuFont, stdColour, hvrColour,
            backColour=backColour, onClick=self._toggleSubMenu)

    def _toggleSubMenu(self, element):
        self.gvm.showSubMenu(self)

    def update(self):
        pass

class ReadyMenu(SelectionMenu):
    def __init__(self, gvm, pos):
        self.scratchItem = CountedMenuItem('Ready', True)
        SelectionMenu.__init__(self, gvm, pos, [
            CountedMenuItem('Not ready', False),
            self.scratchItem,
        ])

    def selectItem(self, ready):
        self.gvm.onChange.execute(PlayerIsReadyMsg(self.gvm.playerId, ready))
        self.gvm.hideSubMenu()

    def updateTitle(self, player):
        if player.readyToStart:
            title = 'Ready'
        else:
            title = 'Not ready'
        self.button.setText(title)

    def update(self):
        values = {}
        for player in self.gvm.world.players:
            if not player.bot:
                key = player.readyToStart
                values[key] = values.get(key, 0) + 1

        for item in self.items:
            item.count = values.get(item.action, 0)


class LevelMenu(SelectionMenu):
    def __init__(self, gvm, pos):
        options = [
            ('Auto level', b'auto'),
            ('Trosnoth Match', b'standard'),
            ('Free for All', b'free4all'),
            ('Cat Among Pigeons', b'catpigeon'),
            ('Hunted', b'hunted'),
            ('Orb Chase', b'orbchase'),
            ('Elephant King', b'elephantking'),
            ('Trosball', b'trosball'),
        ]

        SelectionMenu.__init__(self, gvm, pos, [
            CountedMenuItem(name, key) for name, key in options])
        self.nameMap = {key: name for name, key in options}

    def selectItem(self, levelCode):
        self.gvm.onChange.execute(
            SetPreferredLevelMsg(self.gvm.playerId, levelCode))
        self.gvm.hideSubMenu()

    def updateTitle(self, player):
        self.button.setText(self.nameMap[player.preferredLevel])

    def update(self):
        values = {}
        for player in self.gvm.world.players:
            if not player.bot:
                key = player.preferredLevel
                values[key] = values.get(key, 0) + 1

        for item in self.items:
            item.count = values.get(item.action, 0)


class TeamMenu(SelectionMenu):
    def __init__(self, gvm, pos):
        items = [
            CountedMenuItem('Any team', ''),
            MenuItem('---', None),
            MenuItem('Other...', None, listener=self._otherClicked),
        ]
        SelectionMenu.__init__(self, gvm, pos, items)

    def updateTitle(self, player):
        if player.preferredTeam == '':
            title = 'Any team'
        else:
            title = player.preferredTeam
        self.button.setText(title)

    def _otherClicked(self, item):
        prompt = TeamNameBox(self.gvm.app)
        @prompt.onClose.addListener
        def _customEntered():
            if prompt.result == DialogResult.OK:
                team = prompt.value
                self.gvm.onChange.execute(SetPreferredTeamMsg(team.encode(
                    'utf-8')))

        prompt.show()
        self.gvm.hideSubMenu()

    def selectItem(self, team):
        if team is None:
            return
        self.gvm.onChange.execute(SetPreferredTeamMsg(team.encode('utf-8')))
        self.gvm.hideSubMenu()

    def update(self):
        values = {'Humans [HvM]': 0}
        for player in self.gvm.world.players:
            if not player.bot:
                team = player.preferredTeam
                values[team] = values.get(team, 0) + 1
        killable_items = []
        for item in self.items:
            if item.action is None:
                continue
            if item.action in values:
                item.count = values.pop(item.action)
            else:
                item.count = 0
                if item.action != '':
                    killable_items.append(item)
        for item in killable_items:
            self.removeItem(item)
        for team, count in values.items():
            item = CountedMenuItem(team, team)
            item.count = count
            self.insertItem(-2, item)

DEFAULT_MAP_SIZES = (
    ((0, 0), 'Auto size map'),
    ((3, 2), 'Stardard map'),
    ((1, 1), 'Small map'),
    ((5, 1), 'Wide map'),
    ((5, 3), 'Large map'),
)

MAP_SIZE_NAMES = dict(DEFAULT_MAP_SIZES)

class SizeMenu(SelectionMenu):
    def __init__(self, gvm, pos):
        items = []
        for size, name in DEFAULT_MAP_SIZES:
            items.append(CountedMenuItem(name, size))
        items.extend([
            MenuItem('---', None),
            MenuItem('Other...', None, listener=self._otherClicked),
        ])
        SelectionMenu.__init__(self, gvm, pos, items)

    def updateTitle(self, player):
        title = MAP_SIZE_NAMES.get(player.preferredSize)
        if title is None:
            title = '%d x %d map' % player.preferredSize
        self.button.setText(title)

    def _otherClicked(self, item):
        prompt = MapSizeBox(self.gvm.app)
        @prompt.onClose.addListener
        def _customEntered():
            if prompt.result == DialogResult.OK:
                width, height = prompt.value
                width = max(0, min(10, width))
                height = max(0, min(10, height))
                self.gvm.onChange.execute(SetPreferredSizeMsg(self.gvm.playerId,
                        width, height))

        prompt.show()
        self.gvm.hideSubMenu()

    def selectItem(self, size):
        if size is None:
            return
        self.gvm.onChange.execute(SetPreferredSizeMsg(self.gvm.playerId,
                size[0], size[1]))
        self.gvm.hideSubMenu()

    def update(self):
        values = {}
        for player in self.gvm.world.players:
            if not player.bot:
                size = player.preferredSize
                values[size] = values.get(size, 0) + 1
        killable_items = []
        for item in self.items:
            if item.action is None:
                continue
            if item.action in values:
                item.count = values.pop(item.action)
            else:
                item.count = 0
                if item.action not in MAP_SIZE_NAMES:
                    killable_items.append(item)
        for item in killable_items:
            self.removeItem(item)
        for size, count in values.items():
            item = CountedMenuItem('%d x %d map' % size, size)
            item.count = count
            self.insertItem(-2, item)

class DurationMenu(SelectionMenu):
    def __init__(self, gvm, pos):
        SelectionMenu.__init__(self, gvm, pos, [
            CountedMenuItem('Auto duration', 0),
            MenuItem('---', None),
            MenuItem('Other...', None, listener=self._otherClicked),
        ])

    def updateTitle(self, player):
        duration = player.preferredDuration
        if duration == 0:
            title = 'Auto duration'
        else:
            title = '%d min' % (int(duration/60+0.5),)
        self.button.setText(title)

    def _otherClicked(self, item):
        prompt = GameDurationBox(self.gvm.app)
        @prompt.onClose.addListener
        def _customEntered():
            if prompt.result == DialogResult.OK:
                duration = int(prompt.value) * 60
                self.gvm.onChange.execute(SetPreferredDurationMsg(
                        self.gvm.playerId, duration))

        prompt.show()
        self.gvm.hideSubMenu()


    def selectItem(self, duration):
        if duration is None:
            return
        self.gvm.onChange.execute(SetPreferredDurationMsg(self.gvm.playerId,
                duration))
        self.gvm.hideSubMenu()

    def update(self):
        values = {}
        for player in self.gvm.world.players:
            if not player.bot:
                duration = player.preferredDuration
                values[duration] = values.get(duration, 0) + 1
        killable_items = []
        for item in self.items:
            if item.action is None:
                continue
            if item.action in values:
                item.count = values.pop(item.action)
            else:
                item.count = 0
                if item.action != 0:
                    killable_items.append(item)
        for item in killable_items:
            self.removeItem(item)
        for duration, count in values.items():
            item = CountedMenuItem('%d min' % (int(duration/60+0.5),),
                    duration)
            item.count = count
            self.insertItem(-2, item)

class MapSizeBox(DialogBox):
    def __init__(self, app, width=2, height=1):
        super(MapSizeBox, self).__init__(app, ScaledSize(400,230),
                "Custom Size")
        labelFont = app.screenManager.fonts.bigMenuFont
        labelColour = app.theme.colours.dialogBoxTextColour
        btnFont = app.screenManager.fonts.bigMenuFont
        btnColour = app.theme.colours.dialogButtonColour
        highlightColour = app.theme.colours.black
        inputFont = app.screenManager.fonts.defaultTextBoxFont
        inputColour = app.theme.colours.grey

        self.widthBox = InputBox(app, Region(midleft=self.Relative(0.65, 0.25),
                size=self.Relative(0.15, 0.2)), str(width),
                font=inputFont, colour=inputColour, onClick=self.setFocus,
                onEnter=self.okClicked,
                validator=intValidator, maxLength=2)

        self.heightBox = InputBox(app, Region(midleft=self.Relative(0.65, 0.55),
                size=self.Relative(0.15, 0.2)),
                str(height), font=inputFont, colour=inputColour,
                onClick=self.setFocus, onEnter=self.okClicked,
                validator=intValidator, maxLength=2)

        # Add elements to screen
        self.elements = [
            TextElement(app, 'Half Width:', labelFont,
                Location(self.Relative(0.6, 0.25), 'midright'),
                labelColour),
            self.widthBox,

            TextElement(app, 'Height:', labelFont,
                Location(self.Relative(0.6, 0.55), 'midright'),
                labelColour),
            self.heightBox,

            TextButton(app,
                Location(self.Relative(0.3, 0.9), 'center'),
                'Ok', btnFont, btnColour, highlightColour,
                onClick=self.okClicked),
            TextButton(app,
                Location(self.Relative(0.7, 0.9), 'center'),
                'Cancel', btnFont, btnColour, highlightColour,
                onClick=self.cancelClicked),
            ]

        self.tabOrder = [self.widthBox, self.heightBox]
        self.setFocus(self.widthBox)
        #self.setColours(colours.dialogBoxEdgeColour,
        #        colours.dialogBoxTextColour, colours.dialogBoxTextColour)

    def okClicked(self, element):
        self.result = DialogResult.OK
        self.value = (int(self.widthBox.value), int(self.heightBox.value))
        self.close()

    def cancelClicked(self, element):
        self.result = DialogResult.Cancel
        self.value = None
        self.close()

class EntryDialog(DialogBox):
    def __init__(self, app, title, label, validator=None):
        DialogBox.__init__(self, app, Canvas(400, 230), title)

        labelFont = app.screenManager.fonts.bigMenuFont
        labelColour = app.theme.colours.dialogBoxTextColour
        btnFont = app.screenManager.fonts.bigMenuFont
        btnColour = app.theme.colours.dialogButtonColour
        highlightColour = app.theme.colours.black
        inputFont = app.screenManager.fonts.defaultTextBoxFont
        inputColour = app.theme.colours.grey

        self.inputBox = InputBox(app,
            Region(topleft=self.Relative(0.1, 0.4),
                bottomright=self.Relative(0.9, 0.6)),
            font=inputFont, colour=inputColour, onClick=self.setFocus,
            onEnter=self.okClicked, onEsc=self.cancelClicked,
            validator=validator)

        self.elements = [
            TextElement(app, label,
                labelFont, Location(self.Relative(0.1, 0.2), 'midleft'),
                labelColour),
            self.inputBox,

            TextButton(app,
                Location(self.Relative(0.3, 0.9), 'center'),
                'Ok', btnFont, btnColour, highlightColour,
                onClick=self.okClicked),
            TextButton(app,
                Location(self.Relative(0.7, 0.9), 'center'),
                'Cancel', btnFont, btnColour, highlightColour,
                onClick=self.cancelClicked),
        ]

        self.setFocus(self.inputBox)

    def okClicked(self, element):
        self.result = DialogResult.OK
        self.value = self.inputBox.value
        self.close()

    def cancelClicked(self, element):
        self.result = DialogResult.Cancel
        self.value = self.inputBox.value
        self.close()


class TeamNameBox(EntryDialog):
    def __init__(self, app):
        EntryDialog.__init__(self, app, 'Custom Team', 'Team name:')


class GameDurationBox(EntryDialog):
    def __init__(self, app):
        EntryDialog.__init__(self, app, 'Custom Duration', 'Duration (mins):',
                intValidator)


class NicknameBox(EntryDialog):
    def __init__(self, app, nick, head):
        title = 'Player settings'
        DialogBox.__init__(self, app, Canvas(400, 290), title)

        labelFont = app.screenManager.fonts.bigMenuFont
        labelColour = app.theme.colours.dialogBoxTextColour
        btnFont = app.screenManager.fonts.bigMenuFont
        btnColour = app.theme.colours.dialogButtonColour
        highlightColour = app.theme.colours.black
        inputFont = app.screenManager.fonts.defaultTextBoxFont
        inputColour = app.theme.colours.grey

        self.inputBox = InputBox(
            app,
            Region(
                topleft=self.Relative(0.1, 0.25),
                bottomright=self.Relative(0.9, 0.45)),
            nick,
            font=inputFont, colour=inputColour, onClick=self.setFocus,
            onEnter=self.ok_clicked, onEsc=self.cancel_clicked,
        )

        self.heads = HeadSelector(app, Region(
            topleft=self.Relative(0.1, 0.5),
            bottomright=self.Relative(0.9, 0.8)))
        self.heads.selected(head)

        self.elements = [
            TextElement(
                app, 'Nickname:',
                labelFont, Location(self.Relative(0.1, 0.15), 'midleft'),
                labelColour),
            self.inputBox,
            self.heads,

            TextButton(
                app,
                Location(self.Relative(0.3, 0.9), 'center'),
                'Ok', btnFont, btnColour, highlightColour,
                onClick=self.ok_clicked),
            TextButton(
                app,
                Location(self.Relative(0.7, 0.9), 'center'),
                'Cancel', btnFont, btnColour, highlightColour,
                onClick=self.cancel_clicked),
        ]

        self.setFocus(self.inputBox)

    def ok_clicked(self, element):
        self.result = DialogResult.OK
        self.value = self.inputBox.value, self.heads.getSelectedValue()
        self.close()

    def cancel_clicked(self, element):
        self.result = DialogResult.Cancel
        self.value = self.inputBox.value, self.heads.getSelectedValue()
        self.close()

