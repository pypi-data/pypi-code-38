import pygame

from trosnoth.gui.framework.elements import TextButton
from trosnoth.gui.common import (Location, ScaledSize,
        ScaledScreenAttachedPoint)


def mainButton(app, text, onClick, pos, anchor='topleft', hugeFont=False,
        smallFont=False):
    pos = Location(ScaledScreenAttachedPoint(ScaledSize(pos[0], pos[1]),
            'topleft'), anchor)
    if hugeFont:
        font = app.screenManager.fonts.hugeMenuFont
    elif smallFont:
        font = app.screenManager.fonts.menuFont
    else:
        font = app.screenManager.fonts.mainMenuFont
    result = TextButton(app, pos, text, font, app.theme.colours.mainMenuColour,
            app.theme.colours.mainMenuHighlight)
    result.onClick.addListener(lambda sender: onClick())
    return result


def button(app, text, onClick, pos, anchor='topleft', hugeFont=False,
        smallFont=False, firstColour=None, secondColour=None):
    if firstColour is None:
        firstColour = app.theme.colours.secondMenuColour
    if secondColour is None:
        secondColour = app.theme.colours.mainMenuHighlight
    pos = Location(ScaledScreenAttachedPoint(ScaledSize(pos[0], pos[1]),
            anchor), anchor)
    if hugeFont:
        font = app.screenManager.fonts.hugeMenuFont
    elif smallFont:
        font = app.screenManager.fonts.menuFont
    else:
        font = app.screenManager.fonts.mainMenuFont
    result = TextButton(app, pos, text, font, firstColour, secondColour)
    result.onClick.addListener(lambda sender: onClick())
    return result


def setAlpha(surface, alpha, alphaSurface=None):
    '''
    Sets the alpha of the given surface, even if it already has per-pixel
    alpha.
    Note that if per-pixel alphas are enabled, this will actually change the
    transparency of the pixels in the image, so calling it again with alpha=255
    will not reverse it.
    '''
    if surface.get_flags() & pygame.SRCALPHA:
        if alpha >= 255:
            return
        if not alphaSurface:
            alphaSurface = pygame.Surface(
                surface.get_rect().size, pygame.SRCALPHA)

        alphaSurface.fill((255, 255, 255, alpha))
        surface.blit(
            alphaSurface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    else:
        if alpha >= 255:
            alpha = None
        surface.set_alpha(alpha)
