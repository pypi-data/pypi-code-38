from trosnoth.const import MAP_TO_SCREEN_SCALE


def mapPosToScreen(pt, focus, area):
    return (int((pt[0] - focus[0]) * MAP_TO_SCREEN_SCALE + area.centerx + 0.5),
            int((pt[1] - focus[1]) * MAP_TO_SCREEN_SCALE + area.centery + 0.5))


def mapPosToPanda(pt):
    x, z = mapSizeToPanda(pt)
    return (x, 0, z)


def mapSizeToPanda(size):
    w, h = size
    return (w / 16., h / -16.)
