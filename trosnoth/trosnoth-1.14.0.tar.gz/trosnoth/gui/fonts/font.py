from trosnoth.gui.fonts import fontcache

class Font(object):
    def __init__(self, name, size, bold = False):
        self._name = name
        self._size = size
        self._bold = bold
        self._app = None
        self._filename = None

    def render(self, app, text, antialias, colour, background=None):
        if background==None:
            return self._getFont(app).render(text, antialias, colour)
        else:
            return self._getFont(app).render(text, antialias, colour,
                    background)

    def size(self, app, text):
        return self._getFont(app).size(text)

    def getLineSize(self, app):
        return self._getFont(app).get_linesize()

    def getHeight(self, app):
        return self._getFont(app).get_height()

    def _getFont(self, app):
        if app != self._app:
            filename = self._filename = app.getFontFilename(self._name)
            self._app = app
        else:
            filename = self._filename
        return fontcache.get(filename, self._size, self._bold)

    def __repr__(self):
        return 'Font: %s size %d' % (self._name, self._size)

class ScaledFont(Font):
    def _getFont(self, app):
        if app != self._app:
            filename = self._filename = app.getFontFilename(self._name)
            self._app = app
        else:
            filename = self._filename
        return fontcache.get(filename,
                int(self._size * app.screenManager.scaleFactor + 0.5),
                self._bold)

    def __repr__(self):
        return 'Scaled Font: %s size %d' % (self._name, self._size)
