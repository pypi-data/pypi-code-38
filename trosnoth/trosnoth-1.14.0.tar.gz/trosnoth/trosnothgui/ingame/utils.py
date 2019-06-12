import pygame

from trosnoth.const import MAP_TO_SCREEN_SCALE

def blitPart(surface, source, dest, part):
    '''
    Performs a blit, positioning the source on the surface as for
    surface.blit(source, dest), but only blits the subrect part. part is a rect
    relative to the top-left corner of the source image.
    '''
    surface.blit(source, (dest[0] + part.left, dest[1] + part.top), part)


def viewRectToMap(focus, area):
    pos = screenToMapPos(area.topleft, focus, area)
    size = (
        int(area.width / MAP_TO_SCREEN_SCALE + 0.5),
        int(area.height / MAP_TO_SCREEN_SCALE + 0.5))
    return pygame.Rect(pos, size)


def zonePosToScreen(pt, focus, area):
    return mapPosToScreen((pt[0] - 1024, pt[1] - 384), focus, area)


def mapPosToScreen(pt, focus, area):
    return (int((pt[0] - focus[0]) * MAP_TO_SCREEN_SCALE + area.centerx + 0.5),
            int((pt[1] - focus[1]) * MAP_TO_SCREEN_SCALE + area.centery + 0.5))


def screenToMapPos(pt, focus, area):
    return (int((pt[0] - area.centerx) / MAP_TO_SCREEN_SCALE + 0.5) + focus[0],
            int((pt[1] - area.centery) / MAP_TO_SCREEN_SCALE + 0.5) + focus[1])