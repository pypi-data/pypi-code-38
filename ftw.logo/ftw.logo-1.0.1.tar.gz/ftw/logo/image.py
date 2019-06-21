from wand.image import Image
import os


class Image(Image):

    def __init__(self, **kwargs):
        self.filename = kwargs.get("filename", None)
        # behind format is a setter so the extension has to be kept seperately
        self.extension = kwargs.pop("extension", None)
        if self.filename and not os.path.isfile(self.filename):
            raise ValueError('{} could not be found'.format(self.filename))  # pragma: no cover

        super(Image, self).__init__(**kwargs)
        if self.filename:
            if self.extension is None:
                _, extension = os.path.splitext(self.filename)
                self.extension = extension.lstrip('.')

            self.format = self.extension

        self._blob = None

    def make_blob(self):
        if self._blob:
            return self._blob
        if self.extension == 'svg' and self.filename:
            # If the target extension is svg, and we assume that the input data is also svg,
            # we don't need to transform anything, but we can simply return the original data
            # read from self.filename.
            # self contains the image, but it is already converted to MVG, but we cannot
            # convert it back to SVG. Therefore we need to read the original.
            with open(self.filename, 'r') as f:
                self._blob = f.read()
        else:
            self._blob = super(Image, self).make_blob(self.extension)
        return self._blob

    def append(self, other):
        self.sequence.append(other)
