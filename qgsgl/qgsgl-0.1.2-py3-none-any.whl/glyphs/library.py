from PyQt5.QtGui import QFont


class FontLibrary:
    def __init__(self, default_face='Open Sans'):
        self._default_face = default_face
        self._font_library = {}

    @property
    def available_face(self):
        return [key for key in self._font_library.keys()]

    def add_font(self, name, face, weights, italic):
        for weight in weights:
            self._font_library.setdefault(
                face, {}).setdefault(
                    weight, {}).setdefault(italic, name)

    def get_font_name(self, face, weight, italic):
        face = self._font_library.get(face) if self._font_library.get(face) \
                is not None else self._font_library.get(self._default_face)
        # TODO: Find a better way to get the weight
        find_weight = True
        reached_zero = False
        while find_weight:
            if face.get(weight) is None:
                if weight > 0 and not reached_zero:
                    weight -= 1
                else:
                    reached_zero = True
                    weight += 1
            else:
                weight = face.get(weight)
                find_weight = False

        return weight.get(italic) if weight.get(italic) \
            is not None else weight.get(not italic)


if __name__ == '__main__':
    font = FontLibrary(default_face='Open Sans')
    font.add_font('Open Sans Light Italic',
                  'Open Sans',
                  [QFont.Thin, QFont.ExtraLight, QFont.Light],
                  True)
    font.add_font('Open Sans Light',
                  'Open Sans',
                  [QFont.Thin, QFont.ExtraLight, QFont.Light],
                  False)
    print(font.get_font_name('Open Sans', QFont.Light, True))
