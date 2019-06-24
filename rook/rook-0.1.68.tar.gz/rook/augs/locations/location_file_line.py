import inspect
import hashlib
import sys

import six
import os

from rook.services.bdb_location_service import BdbLocationService
from rook.services.import_service import ImportService

from rook.exceptions import RookHashFailedException, RookHashMismatchException, \
    RookHashCalculationFailed, RookSourceFileNotFound

from rook.logger import logger
from rook.processor.error import Error


class LocationFileLine(object):

    NAME = 'file_line'

    def __init__(self, arguments, processor_factory=None):
        self.filename = arguments.get('filename')
        # If we have a filename, make sure pyc is removed
        if self.filename:
            if isinstance(self.filename, str):
                # Some BDBs identify files by ID
                self.filename = self.filename.replace('.pyc', '.py')

        if self.filename is None:
            self.module_name = arguments['module_name'].lower()
        else:
            self.module_name = None

        self.lineno = arguments['lineno']

        self.file_hash = arguments.get('sha256')

        self.include_externals = arguments.get('includeExternals')
        if self.include_externals is None:
            # The only case it will be equal to '' is when its only filename (without folder, and without '/')
            if self.filename and isinstance(self.filename, str) and os.path.dirname(self.filename) == '':
                self.include_externals = False
            else:
                self.include_externals = True

        # This is to allow tests to reliably hook the file open function
        self.open_file = open

    def add_aug(self, trigger_services, output, aug):
        logger.info("Adding aug")

        def callback(module):
            try:
                self.test_hash(aug, module)

                filepath = inspect.getsourcefile(module)
                if not filepath:
                    if module.__file__.endswith('.pyc'):
                        filepath = module.__file__.replace('.pyc', '.py')

                trigger_services.get_service(BdbLocationService.NAME).add_breakpoint_aug(module, self.lineno,
                                                                                         filepath, aug)
            except Exception as exc:
                message = "Exception when adding aug"
                logger.exception(message)
                aug.set_error(Error(exc=exc, message=message))

        def removed():
            aug.set_removed()

        import_service = trigger_services.get_service(ImportService.NAME)
        if import_service.register_post_import_notification(aug.aug_id, self.module_name, self.filename, self.include_externals, self.lineno, callback, removed):
            aug.set_pending()

    def _normalize_file_contents(self, data):
        if six.PY2:
            string = data.replace('\r\n', '\n').replace('\r\x00\n\x00', '\n\x00').replace('\r', '\n')
        else:
            string = data.decode().replace('\r\n', '\n').replace('\r\x00\n\x00', '\n\x00'). \
                replace('\r', '\n').encode('UTF8')
        return string

    def test_hash(self, aug, module):
        # Don't test if we don't have a hash
        if not self.file_hash:
            return

        filepath = inspect.getsourcefile(module)
        if not filepath:
            if module.__file__.endswith('.pyc'):
                aug.send_warning(Error(exc=RookSourceFileNotFound(module.__file__)))
                return
            raise RookHashFailedException(module.__name__)

        try:
            with self.open_file(filepath, 'rb') as f:
                string = f.read()
        except IOError as exc:
            # if reading the file has failed, it might be because it's a zipimport.
            # try loading the file contents using the module's loader.
            if not os.path.exists(filepath) and ".zip/" in filepath:
                relative_path = filepath.split(".zip/", 2)[1]
                string = module.__loader__.get_data(relative_path)
            else:
                if not os.path.isfile(filepath):
                    aug.send_warning(Error(exc=RookSourceFileNotFound(module.__file__)))
                    return
                raise RookHashCalculationFailed(filepath, module.__name__, exc)

        string = self._normalize_file_contents(string)

        hash = hashlib.sha256(string).hexdigest()
        if hash != self.file_hash:
            blob_hash = self.get_git_blob_hash(filepath)

            raise RookHashMismatchException(filepath, self.file_hash, hash, blob_hash)

    def get_git_blob_hash(self, file_path):
        return None
