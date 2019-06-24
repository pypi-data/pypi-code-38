import sys
import platform
import inspect
import importlib

import six

from rook.logger import logger
from rook.processor.namespaces.frame_namespace import FrameNamespace
from ..exceptions import RookBdbFailedException


class BdbLocationService(object):
    NAME = "Bdb"

    def __init__(self):
        self._bdb = self._get_bdb().Bdb()
        self._bdb.user_line = user_line

        self._breakpoints = dict()

        self._bdb.set_trace()

    def ignore_current_thread(self):
        self._bdb.ignore_current_thread()

    def add_breakpoint_aug(self, item, lineno, filepath, aug):
        """
        :param item: A module or a code object to add a BP to.
        """
        logger.info("Setting breakpoint (aug ID %s) at %s:%s (%s, object id %u)", aug.aug_id, filepath, lineno,
                    type(item), id(item))

        result = self._bdb.set_break(item, filepath, lineno, aug.aug_id)
        if result:
            raise RookBdbFailedException(result)
        self.mark_aug_active(aug)

    def mark_aug_active(self, aug):
        self._breakpoints[aug.aug_id] = aug
        aug.set_active()

    def remove_aug(self, aug_id):
        # Get current augs in position
        if aug_id not in self._breakpoints:
            return

        aug = self._breakpoints.pop(aug_id)

        self._bdb.clear_break(aug_id)

        # Update status
        aug.set_removed()

    def clear_augs(self):
        # Attempt to clean nicely

        for aug_id in list(self._breakpoints.keys()):
            self.remove_aug(aug_id)

        # Clean hard any left overs
        self._breakpoints = dict()
        self._bdb.clear_all_breaks()

    def close(self):
        self.clear_augs()
        self._bdb.close()

    def get_canonical_path(self, module):
        return self._bdb.canonic(inspect.getsourcefile(module))

    @staticmethod
    def _get_bdb():
        from rook.config import InstrumentationConfig
        if InstrumentationConfig.ENGINE == "auto":
            if 'CPython' == platform.python_implementation() and sys.platform in ('darwin', 'linux2', 'linux'):
                if (six.PY2 and sys.version_info > (2, 7, 0)) or (six.PY3 and sys.version_info >= (3, 5, 0)):
                    from . import google_bdb as bdb
                else:
                    from . import py_bdb as bdb
            else:
                from . import py_bdb as bdb
        else:
            bdb = importlib.import_module(".." + InstrumentationConfig.ENGINE, __name__)

        return bdb


# This function has been moved outside of the class so that it can be pickled
# safely by cloudpickle (which will pickle any objects referred to by its closure)
# When changing it, take care to avoid using references to anything not imported within the function
def user_line(frame, filename, aug_id, lineno=None):
    from rook.logger import logger as user_line_logger
    try:
        from rook.singleton import singleton_obj as singleton
        self = singleton.get_trigger_services().get_service(BdbLocationService.NAME)
        # Some Bdb implementations report line numbers before the break
        frame_namespace = FrameNamespace(frame, lineno)

        effective_lineno = frame_namespace._lineno

        aug = self._breakpoints.get(aug_id)

        if aug:
            aug.execute(frame_namespace, dict())
        else:
            user_line_logger.error("Aug not found! %s@%d (aug id %r)", str(filename), effective_lineno, aug_id)
    except:
        user_line_logger.exception("Error while processing breakpoint")