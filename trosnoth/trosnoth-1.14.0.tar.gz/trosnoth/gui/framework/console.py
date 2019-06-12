# Trosnoth (UberTweak Platform Game)
# Copyright (C) 2006-2012 Joshua D Bartlett
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

'''
Originally based on the Python code module.
'''

from code import InteractiveConsole
import logging
import sys

import pygame
from twisted.internet import defer

from trosnoth.gui.framework import framework
from trosnoth.gui.framework.prompt import InputBox
from trosnoth.gui.common import ScaledArea


log = logging.getLogger(__name__)


def softspace(file, newvalue):
    oldvalue = 0
    try:
        oldvalue = file.softspace
    except AttributeError:
        pass
    try:
        file.softspace = newvalue
    except (AttributeError, TypeError):
        # "attribute-less object" or "read-only attributes"
        pass
    return oldvalue

class TwistedInteractiveConsole(InteractiveConsole):
    """Closely emulate the behavior of the interactive Python interpreter.

    This class builds on InteractiveInterpreter and adds prompting
    using the familiar sys.ps1 and sys.ps2, and input buffering.

    """

    def __init__(self, *args, **kwargs):
        InteractiveConsole.__init__(self, *args, **kwargs)
        self._dummyStdOut = DummyStdOut(self.write)

    @defer.inlineCallbacks
    def interact(self, banner=None):
        """Closely emulate the interactive Python console.

        The optional banner argument specify the banner to print
        before the first interaction; by default it prints a banner
        similar to the one printed by the real Python interpreter,
        followed by the current class name in parentheses (so as not
        to confuse this with the real interpreter -- since it's so
        close!).

        """
        try:
            sys.ps1
        except AttributeError:
            sys.ps1 = '>>> '
        try:
            sys.ps2
        except AttributeError:
            sys.ps2 = '... '
        cprt = ('Type "help", "copyright", "credits" or "license" for more '
                'information.')
        if banner is None:
            self.write('Python %s on %s\n%s\n(%s)\n' %
                       (sys.version, sys.platform, cprt,
                        self.__class__.__name__))
        else:
            self.write('%s\n' % str(banner))
        more = 0
        while 1:
            try:
                if more:
                    prompt = sys.ps2
                else:
                    prompt = sys.ps1
                try:
                    line = yield self.raw_input(prompt)

                    # Can be None if sys.stdin was redefined
                    encoding = getattr(sys.stdin, 'encoding', None)
                    if encoding and not isinstance(line, str):
                        line = line.decode(encoding)
                except EOFError:
                    self.write('\n')
                    break
                else:
                    try:
                        more = self.push(line)
                    except SystemExit:
                        break
            except KeyboardInterrupt:
                self.write('\nKeyboardInterrupt\n')
                self.resetbuffer()
                more = 0

    def raw_input(self, prompt=''):
        """Write a prompt and read a line.

        The returned line does not include the trailing newline.
        When the user enters the EOF key sequence, EOFError is raised.

        The base implementation uses the built-in function
        raw_input(); a subclass may replace this with a different
        implementation.

        """
        return defer.succeed(input(prompt))

    def runcode(self, code):
        stdout = sys.stdout
        sys.stdout = self._dummyStdOut
        try:
            return InteractiveConsole.runcode(self, code)
        finally:
            sys.stdout = stdout

class DummyStdOut(object):
    def __init__(self, write):
        self.write = write
    def flush(self):
        pass

class DummyStdIn(object):
    def __init__(self, read):
        self.read = read

    def readline(self):
        result = ''
        while True:
            c = self.read(1)
            result += c
            if result in ('', '\n'):
                return result

class TrosnothInteractiveConsole(TwistedInteractiveConsole,
        framework.Element):

    def __init__(self, app, font, area, colour=(192,192,192),
            backColour=(0, 64, 0), historyLimit=2000,
            locals={}):
        TwistedInteractiveConsole.__init__(self, locals=locals)
        framework.Element.__init__(self, app)

        self.font = font
        self.area = area
        self.colour = colour
        self.backColour = backColour
        self.rect = None
        self.image = None
        self.dirty = True
        self.history = ['']
        self.historyLimit = historyLimit
        self.inBox = ib = InputBox(self.app, ScaledArea(0, 0, 1000, 100),
                font=self.font)
        ib.onEnter.addListener(self._enter)
        ib.hasFocus = True
        ib.gotFocus()

        self.readDeferred = None
        self.deferredInputs = []   # List of (prompt, deferred)
        self.font = font
        self.typeAhead = []
        self.inText = ''
        self.cursorPos = 0
        self._dummyStdIn = DummyStdIn(self.stdInRead)
        self._dummyStdIn.deferred_raw_input = self.raw_input

    def raw_input(self, prompt=''):
        """Write a prompt and read a line.

        The returned line does not include the trailing newline.
        When the user enters the EOF key sequence, EOFError is raised.

        The base implementation uses the built-in function
        raw_input(); a subclass may replace this with a different
        implementation.

        """
        if self.readDeferred is not None:
            d = defer.Deferred()
            self.deferredInputs.append((prompt, d))
            return d
        self.write(prompt)
        if len(self.typeAhead) > 0:
            val = self.typeAhead.pop(0)
            return defer.succeed(val)

        self.readDeferred = d = defer.Deferred()
        return d

    def _nextRead(self):
        '''
        Begins the next queued readline if there is one.
        '''
        if len(self.deferredInputs) == 0:
            self.readDeferred = None
            return

        prompt, d = self.deferredInputs.pop(0)
        self.write(prompt)
        self.readDeferred = d

    def _enter(self, box):
        val = box.getValue()
        self.write(val + '\n')
        if self.readDeferred is None:
            self.typeAhead.append(val)
        else:
            d = self.readDeferred
            self._nextRead()
            d.callback(val)
        self.inBox.setValue('')

    def write(self, data):
        data = self.history.pop(-1) + data
        self.history.extend(data.split('\n'))
        self.history = self.history[-self.historyLimit:]
        self.dirty = True

    def runcode(self, code):
        stdin = sys.stdin
        sys.stdin = self._dummyStdIn
        try:
            return TwistedInteractiveConsole.runcode(self, code)
        finally:
            sys.stdin = stdin

    def stdInRead(self, count=None):
        if count is None:
            # Read all the type ahead.
            result = '\n'.join(self.typeAhead) + '\n'
            self.typeAhead[:] = []
        else:
            result = ''
            while len(self.typeAhead) > 0:
                if count <= len(self.typeAhead[0]) + 1:
                    result += self.typeAhead[0][:count]
                    self.typeAhead[0] = self.typeAhead[0][count:]
                    break
                line = self.typeAhead.pop(0)
                count -= len(line) + 1
                result += line + '\n'
        return result

    def draw(self, screen):
        r = self.area.getRect(self.app)
        if r != self.rect:
            self.rect = r
            self.dirty = True
            self.image = pygame.Surface(self.rect.size).convert()
        if self.dirty:
            self._redraw()

        if (self.inText != self.inBox.getValue() or self.cursorPos !=
                self.inBox.cursorIndex):
            self._drawLastLine()

        screen.blit(self.image, self.rect.topleft)

    def processEvent(self, event):
        return self.inBox.processEvent(event)

    def _redraw(self):
        if self.backColour is None:
            self.image.fill((255, 255, 254))
            self.image.set_colorkey((255, 255, 254))
        else:
            self.image.fill(self.backColour)

        y = self.rect.height
        i = len(self.history) - 1
        wrappedLines = []
        while y > 0 and (i >= 0 or len(wrappedLines) > 0):
            if len(wrappedLines) == 0:
                wrappedLines = self._wrapLine(self.history[i])
                i -= 1

            text = wrappedLines.pop()
            if self.backColour is None:
                line = self.font.render(self.app, text, False, self.colour)
            else:
                line = self.font.render(self.app, text, True, self.colour,
                        self.backColour)
            y -= line.get_height()
            self.image.blit(line, (4, y))

        self.dirty = False

    def _wrapLine(self, text):
        '''
        Takes the given line of text, decides where it should be wrapped, and
        returns a list of new lines of text to write.
        '''
        result = []
        indent = 0
        while len(text) > indent:
            n = max(1, self._getLineLength(text))
            if n <= indent * 1.5 and indent > 0:
                text = text[indent:]
                n = max(1, self._getLineLength(text))

            result.append(text[:n])
            if indent == 0:
                indent = 8
                for c in text:
                    if c.isspace():
                        indent += 1
                    else:
                        break
            text = ' ' * indent + text[n:]
        if result == []:
            result = ['']
        return result

    def _getLineLength(self, text):
        '''
        Works out the number of characters into the given string at which the
        string should be wrapped.
        '''
        width = self.rect.width - 8
        result = big = len(text)
        small = 0

        # Binary search to find the largest value that fits in.
        while big != small:
            textWidth = self.font.size(self.app, text[:result])[0]
            if textWidth > width:
                big = result - 1
            else:
                small = result
            result = (big + small + 1) // 2

        result = big
        def doNotSplit(char):
            return char.isalnum() or char in '_\'"'

        if result == len(text) or not doNotSplit(text[result]):
            return result
        while result > 0 and doNotSplit(text[result-1]):
            result -= 1

        if result == 0:
            result = big

        return result

    def _drawLastLine(self):
        self.inText = inText = self.inBox.getValue()
        self.cursorPos = cPos = self.inBox.cursorIndex

        text = self.history[-1] + inText[:cPos] + '|' + inText[cPos:]
        if self.backColour is None:
            line = self.font.render(self.app, text, False, self.colour)
        else:
            line = self.font.render(self.app, text, True, self.colour,
                    self.backColour)
        fillRect = line.get_rect()
        fillRect.bottom = self.rect.height
        fillRect.width = self.rect.width
        if self.backColour is None:
            self.image.fill((255, 255, 254), fillRect)
        else:
            self.image.fill(self.backColour, fillRect)
        self.image.blit(line, (4, fillRect.top))

