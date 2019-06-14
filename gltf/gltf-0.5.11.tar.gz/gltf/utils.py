import os
import base64


def binary_to_uri(b, mime_type='application/octet-stream'):
    return 'data:{};base64,{}'.format(mime_type, base64.b64encode(b).decode('utf-8'))


def load_uri(s, folder=None):
    if s.startswith('data:'):
        return base64.b64decode(s[s.index(',') + 1:])

    if folder:
        s = os.path.join(folder, s)
    with open(s, 'rb') as f:
        return f.read()


class BaseGLTFStructure(object):
    name = None

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False

        return self.__dict__ == other.__dict__
