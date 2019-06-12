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

import platform
import webbrowser

import pygame

def openPage(app, url):
    # If we're in fullscreen, minimise.
    if app.screenManager.isFullScreen():
        if platform.system() != 'Darwin':
            # Try minimising.
            pygame.display.iconify()
        else:
            # .iconify() has problems on Mac OSX

            from trosnoth.gui.framework.dialogbox import OkBox
            from trosnoth.gui.common import ScaledSize
            # Switch out of full screen.
            app.displaySettings.fullScreen = False
            app.displaySettings.apply()
            box = OkBox(app, ScaledSize(600, 300),
                'Web browser opened',
                'Please refer to web browser.'
            )
            def revert():
                # Switch back to full screen.
                app.displaySettings.fullScreen = True
                app.displaySettings.apply()
            box.onClose.addListener(revert)
            box.show()

    # Open in a new tab if possible.
    try:
        webbrowser.open_new_tab(url)
    except AttributeError:
        webbrowser.open_new(url)
