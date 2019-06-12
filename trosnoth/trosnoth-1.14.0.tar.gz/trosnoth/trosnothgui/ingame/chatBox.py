'''chatBox.py - defines the ChatBox class which deals with drawing the
chat box (the box in which you input chat) to the screen.'''

import logging

import pygame

import trosnoth.gui.framework.framework as framework
from trosnoth.gui.framework.elements import TextElement
from trosnoth.gui.framework.prompt import InputBox
from trosnoth.gui.common import Area, FullScreenAttachedPoint, Location
from trosnoth.trosnothgui.ingame.messagebank import MessageBank
from trosnoth.utils.utils import wrapline

log = logging.getLogger()


class ChatBox(framework.CompoundElement):
    def __init__(self, app, world, interface):
        super(ChatBox, self).__init__(app)

        self.world = world
        self.app = app
        self.interface = interface

        self.font = self.app.screenManager.fonts.newChatFont

        self.frameColour = self.app.theme.colours.chatFrameColour
        self.insideColour = self.app.theme.colours.chatInsideColour
        self.textColour = self.app.theme.colours.chatNormalColour

        self.sayToTeam = TextElement(self.app,
            text="Say to team:",
            font=self.font,
            pos=Location(FullScreenAttachedPoint((20, 501), 'topleft'),
                'topleft'),
            colour=self.textColour,
            shadow=True,
        )

        self.inputPosition = Area(FullScreenAttachedPoint((145, 500),
            'topleft'), (370,20), 'topleft')
        self.input = InputBox(self.app, self.inputPosition, font=self.font)
        self.input.onEnter.addListener(lambda sender:
                self.hitEnter(sender.value))
        self.input.onEsc.addListener(lambda sender: self.close())
        self.input.onClick.addListener(self.setFocus)

        self.messages = MessageBank(self.app, 10, 100,
                Location(FullScreenAttachedPoint((20,470),'topleft'),
                'topleft'), 'left', 'bottom', self.font)

        self._chatOpen = False
        self.teamChat = True
        self.player = None

        self.messageBuffer = []

        self.MESSAGE_GAP = self.font.getHeight(self.app)

        self.elements = [self.messages]

    def setPlayer(self, player):
        self.player = player
        if self.player.team is None:
            self.refreshMode()

    def canTeamChat(self):
        return self.player and self.player.team is not None

    def switchModes(self):
        self.teamChat = not self.teamChat
        self.refreshMode()

    def refreshMode(self):
        self.teamChat = self.teamChat and self.canTeamChat()
        if self.teamChat:
            self.sayToTeam.setText('Say to team:')
        else:
            self.sayToTeam.setText('Say to all:')

    def hitEnter(self, senderValue):
        if senderValue.strip() != '':
            self.sendChat(senderValue)
        self.input.clear()

    def sendChat(self, senderValue):
        # Interpret lines with initial hash.
        if senderValue.startswith('#'):
            i = 1
            while senderValue[i:i+1].isdigit():
                i += 1
            try:
                playerId = bytes([int(senderValue[1:i])])
            except ValueError:
                pass
            else:
                self.interface.sendPrivateChat(self.player, playerId,
                        senderValue[i:].lstrip())
                return

        if self.teamChat:
            self.interface.sendTeamChat(self.player, senderValue)
        else:
            self.interface.sendPublicChat(self.player, senderValue)

    def refresh(self):
        if not self.isOpen():
            return
        self.elements = [self.sayToTeam, self.input]

        initialY = 470
        count = 0
        for text, nick, colour, firstLine in reversed(self.messageBuffer):
            currentY = initialY - count * self.MESSAGE_GAP
            if currentY < 200 or count >= 10:
                break

            if firstLine and nick is not None:
                person = TextElement(self.app,
                    text=nick, font=self.font,
                    pos=Location(FullScreenAttachedPoint((20, currentY),
                        'topleft'), 'topleft'),
                    colour=colour,
                    shadow=True,
                )

                xOffset = person._getRect().width
                self.elements.append(person)

                text = text[len(nick):]

            else:
                xOffset = 0

            if nick is None:
                colour = self.app.theme.colours.serverChat
            else:
                colour = self.textColour

            message = TextElement(self.app,
                text=text,
                font=self.font,
                pos=Location(FullScreenAttachedPoint((20 + xOffset,
                    currentY), 'topleft'), 'topleft'),
                colour=colour,
                shadow=True,
            )
            self.elements.append(message)
            count += 1

    def open(self):
        self._chatOpen = True
        self.refresh()
        self.setFocus(self.input)
        self.input.clear()

    def close(self):
        self._chatOpen = False
        self.elements = [self.messages]
        pygame.key.set_repeat()

    def isOpen(self):
        return self._chatOpen

    def newMessage(self, message, nick, colour):

        message = nick + message

        wrappedMessage = wrapline(message, self.font._getFont(self.app), 480)

        # Update the "box open" message elements
        firstLine = True
        for line in wrappedMessage:
            self.messageBuffer.append((line, nick, colour, firstLine))
            firstLine = False

        while len(self.messageBuffer) > 100:
            self.messageBuffer.pop(0)

        # Update the "box closed" message elements
        firstLine = wrappedMessage.pop(0)[len(nick):]
        parts = [(nick, colour), (firstLine, self.textColour)]

        self.messages.newColourMessage(parts)

        for line in wrappedMessage:
            self.messages.newMessage(line, self.textColour)

        self.refresh()

    def newServerMessage(self, message):
        '''Server messages don't follow the format of normal messages and
        require special attention to display.'''

        colour = self.app.theme.colours.serverChat
        wrappedMessage = wrapline("SERVER" + message,
                self.font._getFont(self.app), 480)

        # Update the "box open" message elements
        firstLine = True
        for line in wrappedMessage:
            self.messageBuffer.append((line, None, colour, firstLine))
            firstLine = False

        while len(self.messageBuffer) > 100:
            self.messageBuffer.remove(0)

        # Update the "box closed" message elements
        for line in wrappedMessage:
            self.messages.newMessage(line, colour)

        self.refresh()

    def _getRect(self):
        return self.area.getRect(self.app)

    def draw(self, surface):

        if self._chatOpen:

            pointX = 5
            pointY = 300

            # Draw the frame first
            frame = pygame.Surface((520,230))
            frame.fill(self.frameColour)

            mainBox = pygame.Surface((500, 180))
            mainBox.fill(self.insideColour)

            sayBox = pygame.Surface((120, 20))
            sayBox.fill(self.insideColour)

            if self.app.displaySettings.alphaOverlays:
                mainBox.set_alpha(128)
                sayBox.set_alpha(128)
                frame.set_alpha(128)

            surface.blit(frame, (pointX, pointY))
            surface.blit(mainBox, (pointX + 10, pointY + 10))
            surface.blit(sayBox, (pointX + 10, pointY + 200))

        super(ChatBox, self).draw(surface)

    def processEvent(self, event):
        if not self.isOpen():
            return event

        if event.type == pygame.KEYDOWN and event.key in (pygame.K_LCTRL,
                pygame.K_RCTRL):
            self.switchModes()
        else:
            return self.input.processEvent(event)
