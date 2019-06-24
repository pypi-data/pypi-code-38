from .namespace import Namespace
from .collection_namespace import ListNamespace
from .container_namespace import ContainerNamespace


class StackNamespace(Namespace):
    DEFAULT_TRACEBACK_DEPTH = 1000
    DEFAULT_FRAMES_DEPTH = 100

    def __init__(self, frame):
        super(StackNamespace, self).__init__(self.METHODS)
        self._frame = frame

    def read_attribute(self, name):
        raise NotImplementedError("StackNamespace does not support attribute read!")

    def read_key(self, key):
        pos = int(key)

        current_frame = self._frame

        for i in range(pos):
            current_frame = current_frame.f_back()

        return current_frame

    def traceback(self, args=None):
        if args:
            depth = int(args)
        else:
            depth = self.DEFAULT_TRACEBACK_DEPTH

        result = []

        current_frame = self._frame

        for i in range(depth):
            module = current_frame.module()

            result.append(ContainerNamespace({
                'module': module,
                'filename': current_frame.filename(),
                'line': current_frame.line(),
                'function': current_frame.function()
            }))

            current_frame = current_frame.f_back()

            if not current_frame:
                break

        return ListNamespace(result)

    def frames(self, args=None):
        if args:
            depth = int(args)
        else:
            depth = self.DEFAULT_FRAMES_DEPTH

        result = []

        current_frame = self._frame

        for i in range(depth):
            result.append(current_frame.dump(None))

            current_frame = current_frame.f_back()

            if not current_frame:
                break

        return ListNamespace(result)

    METHODS = (traceback, frames)
