import logging

from trosnoth.model.utils import Rect

from trosnoth.const import HEADS_ORDER
from trosnoth.trosnothgui.pregame.imageRadioButton import (
    RadioButtonGroup,
    ImageRadioButton,
)

from trosnoth.gui.framework.dialogbox import (
    DialogBox, DialogResult, DialogBoxAttachedPoint,
)
from trosnoth.gui.common import (
    ScaledSize, Area, ScaledLocation, Location, SizedImage, LetterboxedArea,
)
from trosnoth.gui.framework import elements, prompt

log = logging.getLogger(__name__)


SpectateResult = object()


class HeadArea:
    def __init__(self, area, index, total):
        self.area = area
        self.index = index
        self.total = total

    def getRect(self, app):
        full_rect = self.area.getRect(app)
        x0 = full_rect.left
        dx0 = int(full_rect.width * self.index / self.total + 0.5)
        dx1 = int(full_rect.width * (self.index + 1) / self.total + 0.5)
        result = Rect(x0 + dx0, full_rect.top, dx1 - dx0, full_rect.height)
        return result

    def getSize(self, app):
        return self.getRect(app).size


class HeadSelector(RadioButtonGroup):
    def __init__(self, app, area):
        super().__init__(app)

        images = [app.theme.sprites.head_pic(head) for head in HEADS_ORDER]
        ratio = len(images) * images[0].get_width() / images[0].get_height()
        full_area = LetterboxedArea(area, ratio)
        for i, head in enumerate(HEADS_ORDER):
            head_area = HeadArea(full_area, i, len(images))
            button = ImageRadioButton(
                app, '', head_area,
                SizedImage(images[i], head_area, alpha=True),
                value=head)
            self.add(button)


class JoinGameDialog(DialogBox):
    def __init__(self, app, controller, world):
        super(JoinGameDialog, self).__init__(
            app, ScaledSize(512, 374), 'Join Game')
        self.world = world
        self.result = None
        self.controller = controller
        self.selectedTeam = None

        fonts = self.app.screenManager.fonts
        self.nickBox = prompt.InputBox(
            self.app,
            Area(
                DialogBoxAttachedPoint(self, ScaledSize(0, 40), 'midtop'),
                ScaledSize(200, 60), 'midtop'),
            '',
            font=fonts.menuFont,
            maxLength=30,
        )
        self.nickBox.onClick.addListener(self.setFocus)
        self.nickBox.onTab.addListener(lambda sender: self.clearFocus())
        name = app.identitySettings.nick
        if name is not None:
            self.nickBox.setValue(name)

        colours = app.theme.colours
        self.cantJoinYet = elements.TextElement(
            self.app,
            '',
            fonts.ingameMenuFont,
            ScaledLocation(256, 115, 'center'),
            colours.cannotJoinColour,
        )

        self.heads = HeadSelector(app, Area(
            # Position within dialog box
            DialogBoxAttachedPoint(self, ScaledSize(0, 130), 'midtop'),
            # Area
            ScaledSize(1024, 50), 'center'))
        self.heads.selected(app.identitySettings.head)

        teamA = world.teams[0]
        teamB = world.teams[1]

        self.joinButtons = {
            teamA: elements.TextButton(
                self.app,
                Location(
                    DialogBoxAttachedPoint(
                        self, ScaledSize(-25, 220), 'midtop'),
                    'topright'),
                str(teamA),
                fonts.menuFont,
                colours.team1msg,
                colours.white,
                onClick=lambda obj: self.joinTeam(teamA)
            ),
            teamB: elements.TextButton(
                self.app,
                Location(
                    DialogBoxAttachedPoint(
                        self, ScaledSize(25, 220), 'midtop'),
                    'topleft'),
                str(teamB),
                fonts.menuFont,
                colours.team2msg,
                colours.white,
                onClick=lambda obj: self.joinTeam(teamB)
            ),
        }
        self.autoJoinButton = elements.TextButton(
            self.app,
            Location(
                DialogBoxAttachedPoint(
                    self, ScaledSize(-25, 270), 'midtop'),
                'topright'),
            'Automatic',
            fonts.menuFont,
            colours.inGameButtonColour,
            colours.white,
            onClick=lambda obj: self.joinTeam()
        )

        self.elements = [
            elements.TextElement(
                self.app,
                'Please enter your nick:',
                fonts.smallMenuFont,
                Location(
                    DialogBoxAttachedPoint(self, ScaledSize(0, 10), 'midtop'),
                    'midtop'),
                colours.black,
            ),
            self.nickBox,
            self.cantJoinYet,
            self.heads,
            elements.TextElement(
                self.app,
                'Select team:',
                fonts.smallMenuFont,
                Location(
                    DialogBoxAttachedPoint(self, ScaledSize(0, 190), 'midtop'),
                    'midtop'),
                colours.black,
            ),

            elements.TextButton(
                self.app,
                Location(
                    DialogBoxAttachedPoint(
                        self, ScaledSize(25, 270), 'midtop'),
                    'topleft'),
                'Spectator',
                fonts.menuFont,
                colours.inGameButtonColour,
                colours.white,
                onClick=lambda obj: self.spectate()
            ),

            elements.TextButton(
                self.app,
                Location(
                    DialogBoxAttachedPoint(
                        self, ScaledSize(0, -10), 'midbottom'),
                    'midbottom'),
                'Cancel',
                fonts.menuFont,
                colours.inGameButtonColour,
                colours.white,
                onClick=self.cancel
            )
        ]
        self.setColours(
            colours.joinGameBorderColour,
            colours.joinGameTitleColour,
            colours.joinGameBackgroundColour)
        self.setFocus(self.nickBox)

    def refreshTeamButtons(self):
        allowedTeamIds = self.world.uiOptions.teamIdsHumansCanJoin
        shown = 0
        for team, button in self.joinButtons.items():
            try:
                self.elements.remove(button)
            except ValueError:
                pass
            if team.id in allowedTeamIds:
                button.setText(str(team))
                self.elements.append(button)
                shown += 1

        try:
            self.elements.remove(self.autoJoinButton)
        except ValueError:
            pass
        if len(allowedTeamIds) > 1 or shown == 0:
            self.elements.append(self.autoJoinButton)

    def show(self):
        self.refreshTeamButtons()
        super(JoinGameDialog, self).show()

    def joinTeam(self, team=None):
        self.selectedTeam = team
        self.cantJoinYet.setText('')

        nick = self.nickBox.value
        if nick == '' or nick.isspace():
            # Disallow all-whitespace nicks
            return

        self.result = DialogResult.OK
        self.close()

    def spectate(self):
        self.selectedTeam = None
        self.cantJoinYet.setText('')

        self.result = SpectateResult
        self.close()

    def cancel(self, sender):
        self.result = DialogResult.Cancel
        self.close()


class JoiningDialog(DialogBox):
    def __init__(self, app, controller):
        super(JoiningDialog, self).__init__(
            app, ScaledSize(530, 180), 'Trosnoth')
        colours = app.theme.colours
        self.controller = controller

        fonts = self.app.screenManager.fonts
        self.text = elements.TextElement(
            self.app,
            '',
            fonts.menuFont,
            Location(
                DialogBoxAttachedPoint(self, ScaledSize(0, 40), 'midtop'),
                'midtop'),
            colour=colours.joiningColour,
        )

        self.elements = [
            self.text,
            elements.TextButton(
                self.app,
                Location(
                    DialogBoxAttachedPoint(
                        self, ScaledSize(0, -10), 'midbottom'),
                    'midbottom'),
                'Cancel',
                fonts.menuFont,
                colours.inGameButtonColour,
                colours.white,
                onClick=controller.cancelJoin,
            ),
        ]
        self.setColours(
            colours.joinGameBorderColour,
            colours.joinGameTitleColour,
            colours.joinGameBackgroundColour)

    def show(self, nick):
        self.text.setText('Joining as %s...' % (nick,))
        DialogBox.show(self)
