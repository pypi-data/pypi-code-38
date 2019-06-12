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

import os
import pygame

from trosnoth.gui.framework import framework
from trosnoth.gui.framework.listbox import ListBox
from trosnoth.gui.framework.elements import TextElement
from trosnoth.gui.framework.tab import Tab
from trosnoth.gui.common import ScaledLocation, ScaledArea
from trosnoth.trosnothgui.common import button
from trosnoth.utils.event import Event

from trosnoth.data import getPath, user, makeDirs, themes

class ThemeTab(Tab, framework.TabFriendlyCompoundElement):
    def __init__(self, app, onClose=None, onRestart=None):
        super(ThemeTab, self).__init__(app, 'Themes')

        self.onClose = Event()
        if onClose is not None:
            self.onClose.addListener(onClose)
        self.onRestart = Event()
        if onRestart is not None:
            self.onRestart.addListener(onRestart)

        font = self.app.screenManager.fonts.menuFont
        colours = self.app.theme.colours

        self.inactiveTheme = False
        self.originalTheme = app.theme.name

        # Static text
        self.staticText = [
            TextElement(self.app, 'theme information:', font,
                    ScaledLocation(960, 250, 'topright'),
                    colours.headingColour),
            TextElement(self.app, 'theme contents:', font,
                    ScaledLocation(960, 390, 'topright'),
                colours.headingColour)
        ]

        # Dynamic text
        self.feedbackText = TextElement(self.app, 'Your current theme: %s' %
                (app.theme.name,), font, ScaledLocation(512, 200, 'midtop'),
                colours.startButton)
        self.listHeaderText = TextElement(self.app, 'available themes:', font,
                ScaledLocation(70, 250), colours.headingColour)
        self.themeNameText = TextElement(self.app, 'Default Theme', font,
                ScaledLocation(960, 290, 'topright'), colours.startButton)
        self.themeAuthorText = TextElement(self.app,
                'created by: Trosnoth Team', font,
                ScaledLocation(960, 330, 'topright'), colours.startButton)

        self.contents = []

        numContents = 4
        for yPos in range(430, 430 + numContents * 40 + 1, 40):
            self.contents.append(TextElement(self.app, '', font,
                    ScaledLocation(960, yPos, 'topright'), colours.startButton))

        self.dynamicText = [self.feedbackText, self.listHeaderText,
                self.themeNameText, self.themeAuthorText] + self.contents

        # Theme list
        self.themeList = ListBox(self.app, ScaledArea(70, 290, 400, 290), [],
                font, colours.listboxButtons)
        self.themeList.onValueChanged.addListener(self.updateSidebar)

        # Text buttons
        self.useThemeButton = button(app, 'use selected theme',
                self.applyTheme, (0, -125), 'midbottom')
        self.refreshButton = button(app, 'refresh', self.populateList,
                (-100, -75), 'midbottom')
        self.cancelButton = button(app, 'cancel', self.backToMain, (100, -75),
                'midbottom')
        self.restartButton = button(app, 'restart Trosnoth', self.restart,
                (0, -125), 'midbottom')

        self.buttons = [self.useThemeButton, self.refreshButton,
                self.cancelButton, self.restartButton]

        # Combine the elements
        self.elements = self.staticText + self.dynamicText + self.buttons + [
                self.themeList]

        self.contentTypes = {"sprites": "sprite", "blocks": "map block",
                "fonts": "font", "startupMenu": "backdrop"}

        # Populate the list of replays
        self.populateList()

    def populateList(self):

        defaultTheme = {"name": "Default Theme", "filename": "default",
                "author": "Trosnoth Team", "content": None,
                "source": "internal"}

        # Clear out the sidebar
        self.themeNameText.setText('')
        self.themeAuthorText.setText('')
        for element in self.contents:
            element.setText('')
        self.useThemeButton.setText('')
        self.restartButton.setText('')
        self.listHeaderText.setText('available themes:')
        self.themeList.index = -1

        userThemeDir = getPath(user, 'themes')
        internalThemeDir = getPath(themes)
        makeDirs(userThemeDir)

        themeList = []

        # Get a list of internal themes
        for dirName in os.listdir(internalThemeDir):
            if os.path.isdir(os.path.join(internalThemeDir, dirName)):
                themeList.append("i/%s" % dirName)

        # Get a list of user-defined themes
        for dirName in os.listdir(userThemeDir):
            if os.path.isdir(os.path.join(userThemeDir, dirName)):
                # Internal themes overrule user-defined themes
                if "i/" + dirName not in themeList and dirName != "default":
                    themeList.append("u/%s" % dirName)

        # Assume all themes are valid for now
        validThemes = themeList[:]

        self.themeInfo = {}

        for themeName in themeList:
            themeInfo = {"content": {}}

            if themeName.startswith("i/"):
                themeInfo['source'] = 'internal'
                directory = internalThemeDir
            else:
                themeInfo['source'] = 'user-defined'
                directory = userThemeDir

            themeNameList = themeName
            themeName = themeName[2:]

            themeInfo['filename'] = themeName[2:]

            anyContent = False

            for contentType in list(self.contentTypes.keys()):
                if themeInfo['source'] == 'internal':
                    contentDir = os.path.join(directory, themeName, contentType)
                else:
                    contentDir = os.path.join(directory, themeName, contentType)

                if not os.path.isdir(contentDir):
                    continue
                else:
                    fileCount = len([f for f in os.listdir(contentDir) if
                            os.path.isfile(os.path.join(contentDir, f))])
                    if fileCount > 0:
                        anyContent = True
                        themeInfo["content"][contentType] = fileCount

            if not anyContent:
                validThemes.remove(themeNameList)
                continue

            infoFile = os.path.join(directory, themeName, "info.txt")
            if os.path.isfile(infoFile):
                infoFile = open(infoFile)
                infoContents = infoFile.readlines()
            else:
                infoContents = []

            if len(infoContents) >= 2:
                themeInfo["author"] = infoContents[1].strip()
            else:
                themeInfo["author"] = None

            if len(infoContents) >= 1:
                themeInfo["name"] = infoContents[0].strip()
            else:
                themeInfo["name"] = themeName

            self.themeInfo[themeName] = themeInfo

        self.themeInfo["default"] = defaultTheme

        # Sort the themes alphabetically
        items = [(v['filename'], n) for n, v in self.themeInfo.items()]
        items.sort()
        items = [n for v,n in items]
        self.themeList.setItems(items)

        if len(self.themeInfo) == 1:
            self.listHeaderText.setText("1 available theme:")
            self.themeList.index = 0
            self.updateSidebar(0)
        else:
            self.listHeaderText.setText("%d available themes:" %
                    len(self.themeInfo))

    def updateSidebar(self, listID):
        # Update the details on the sidebar
        displayName = self.themeList.getItem(listID)

        themeInfo = self.themeInfo[displayName]

        if themeInfo['source'] == "internal":
            self.themeNameText.setText(themeInfo['name'] + " (built-in)")
        else:
            self.themeNameText.setText(themeInfo['name'])
        if themeInfo['author'] is not None:
            self.themeAuthorText.setText("by " + themeInfo['author'])
        else:
            self.themeAuthorText.setText("(creator unknown)")

        if themeInfo['content'] is None:
            for element in self.contents:
                element.setText('')
            self.contents[0].setText('N/A')
        else:
            count = 0
            for k, v in themeInfo['content'].items():
                suffix = ""
                if v != 1:
                    suffix = "s"

                text = "%d %s%s" % (v, self.contentTypes[k], suffix)
                self.contents[count].setText(text)
                count += 1

        self.restartButton.setText("")
        if self.app.displaySettings.theme != displayName:
            if displayName == self.originalTheme:
                self.useThemeButton.setText("revert back to this theme")
            else:
                self.useThemeButton.setText("use this theme")
        else:
            self.useThemeButton.setText("")

            if self.inactiveTheme:
                self.restartButton.setText('restart Trosnoth')

    def applyTheme(self):
        themeName = self.themeList.getItem(self.themeList.index)

        self.app.displaySettings.theme = themeName
        self.app.displaySettings.save()

        self.useThemeButton.setText("")

        if themeName != self.originalTheme:
            self.feedbackText.setText("You must restart Trosnoth for the "
                    "'%s' theme to take effect." % themeName)
            self.restartButton.setText('restart Trosnoth')
            self.inactiveTheme = True
        else:
            self.feedbackText.setText('Your current theme: %s' %
                    (self.app.theme.name,))
            self.restartButton.setText("")
            self.inactiveTheme = False

    def restart(self):
        self.onRestart.execute()

    def backToMain(self):
        if self.inactiveTheme:
            self.feedbackText.setText("Your current theme: %s "
                    "(restart required)" % self.app.displaySettings.theme)

        self.onClose.execute()

    def draw(self, surface):
        super(ThemeTab, self).draw(surface)
        width = max(int(3*self.app.screenManager.scaleFactor), 1)
        scalePoint = self.app.screenManager.placePoint
        pygame.draw.line(surface, self.app.theme.colours.mainMenuColour,
                scalePoint((512,260)), scalePoint((512, 580)), width)

