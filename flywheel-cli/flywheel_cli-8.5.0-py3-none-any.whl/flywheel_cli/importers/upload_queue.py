import logging
import os
import tempfile

from abc import ABC, abstractmethod

from .work_queue import Task, WorkQueue
from .packfile import create_zip_packfile
from .progress_reporter import ProgressReporter

log = logging.getLogger(__name__)
MAX_IN_MEMORY_XFER = 32 * (2 ** 20) # Files under 32mb send as one chunk

class Uploader(ABC):
    """Abstract uploader class, that can upload files"""
    verb = 'Uploading'

    @abstractmethod
    def upload(self, container, name, fileobj, metadata=None):
        """Upload the given file-like object to the given container as name.

        Arguments:
            container (ContainerNode): The destination container
            name (str): The file name
            fileobj (obj): The file-like object, which supports read()
            metadata (dict): Container metadata

        Yields:
            int: Number of bytes uploaded (periodically)
        """

    @abstractmethod
    def file_exists(self, container, name):
        """Check if the given file object already exists on the given container.

        Arguments:
            container (ContainerNode): The destination container
            name (str): The file name

        Returns:
            bool: True if the file already exists, otherwise False
        """

    def supports_signed_url(self):
        """Check if signed url upload is supported.

        Returns:
            bool: True if signed url upload is supported
        """
        return False

class UploadFileWrapper(object):
    """Wrapper around file that measures progress"""
    def __init__(self, fileobj=None, walker=None, path=None):
        """Initialize a file wrapper, must specify fileobj OR walker and path"""
        self.fileobj = fileobj
        self.walker = walker
        self.path = path
        self._sent = 0
        self._total_size = None
        if fileobj and fileobj.name:
            self.name = fileobj.name
        else:
            self.name = path

    def _open(self):
        if not self.fileobj:
            self.fileobj = self.walker.open(self.path, 'rb')

    def read(self, size=-1):
        self._open()
        chunk = self.fileobj.read(size)
        self._sent = self._sent + len(chunk)
        return chunk

    def reset(self):
        if self.fileobj:
            self.fileobj.seek(0)
        self._sent = 0

    @property
    def len(self):
        return (self.total_size - self._sent)

    @property
    def total_size(self):
        if self._total_size is None:
            self._open()
            self.fileobj.seek(0,2)
            self._total_size = self.fileobj.tell()
            self.fileobj.seek(0)
        return self._total_size

    def close(self):
        if self.fileobj:
            self.fileobj.close()
        self.fileobj = None

    def get_bytes_sent(self):
        return self._sent


class UploadTask(Task):
    def __init__(self, uploader, audit_log, container, filename, fileobj=None, walker=None, path=None, metadata=None):
        """Initialize an upload task, must specify fileobj OR walker and path"""
        super(UploadTask, self).__init__('upload')
        self.uploader = uploader
        self.audit_log = audit_log
        self.container = container
        self.filename = filename
        self.fileobj = UploadFileWrapper(fileobj=fileobj, walker=walker, path=path)
        self._data = None
        self.metadata = metadata

    def execute(self):
        self.fileobj.reset()

        # Under 32 MB, just read the entire file
        if self.fileobj.len == 0:
            # Skip and log 0-byte files
            log.info('Skipping 0-byte file upload: %s', self.filename)
            self.audit_log.add_log(self.fileobj.name, self.container, self.filename,
                    failed=True, message='Skipped 0-byte file')
            self.skipped = True
        elif self.fileobj.len < MAX_IN_MEMORY_XFER:
            if self._data is None:
                self._data = self.fileobj.read(self.fileobj.len)
            self.uploader.upload(self.container, self.filename, self._data, metadata=self.metadata)
        else:
            self.uploader.upload(self.container, self.filename, self.fileobj, metadata=self.metadata)

        # Safely close the file object
        try:
            self.fileobj.close()
        except:
            log.exception('Cannot close file object')
            pass

        # No more jobs so no priority
        return None, None

    def get_bytes_processed(self):
        return self.fileobj.get_bytes_sent()

    def get_desc(self):
        return 'Upload {}'.format(self.filename)

class PackfileTask(Task):
    def __init__(self, uploader, audit_log, walker, packfile_type, deid_profile,
            container, filename, subdir=None, paths=None, compression=None, max_spool=None):
        super(PackfileTask, self).__init__('packfile')

        self.uploader = uploader
        self.audit_log = audit_log
        self.walker = walker
        self.packfile_type = packfile_type
        self.deid_profile = deid_profile

        self.container = container
        self.filename = filename
        self.subdir = subdir
        self.paths = paths
        self.compression = compression
        self.max_spool = max_spool

        self._bytes_processed = None
        self._logged_error = False

    def execute(self):
        if self.max_spool:
            tmpfile = tempfile.SpooledTemporaryFile(max_size=self.max_spool)
        else:
            tmpfile = tempfile.TemporaryFile()

        # store the packfile path
        audit_path = None
        if self.subdir:
            audit_path = self.subdir
        elif self.paths:
            audit_path = os.path.dirname(self.paths[0])
        else:
            audit_path = self.walker.get_fs_url()

        try:
            zip_member_count = create_zip_packfile(tmpfile, self.walker, packfile_type=self.packfile_type,
                subdir=self.subdir, paths=self.paths, compression=self.compression,
                progress_callback=self.update_bytes_processed, deid_profile=self.deid_profile)
        except Exception as ex:
            log.debug('Error processing packfile at %s', audit_path, exc_info=True)
            if not self._logged_error:
                message = 'Error creating packfile: {}'.format(ex)
                self.audit_log.add_log(audit_path, self.container, self.filename,
                        failed=True, message=message)
                self._logged_error = True
            raise

        #Rewind
        tmpfile.seek(0)

        # Remove walker reference
        self.walker = None

        metadata = {
            'name': self.filename,
            'zip_member_count': zip_member_count
        }

        # The next task is an uplad task
        next_task = UploadTask(self.uploader, self.audit_log, self.container, self.filename,
                          fileobj=tmpfile, metadata=metadata,
                          path=audit_path)

        # Enqueue with higher priority than normal uploads
        return (next_task, 5)

    def get_bytes_processed(self):
        if self._bytes_processed is None:
            return 0
        return self._bytes_processed

    def get_desc(self):
        return 'Pack {}'.format(self.filename)

    def update_bytes_processed(self, bytes_processed):
        self._bytes_processed = bytes_processed


class UploadQueue(WorkQueue):
    def __init__(self, config, audit_log, packfile_count=0, upload_count=0, show_progress=True):
        # Detect signed-url upload and start multiple upload threads
        upload_threads = 1
        uploader = config.get_uploader()
        if uploader.supports_signed_url():
            upload_threads = config.concurrent_uploads

        super(UploadQueue, self).__init__({
            'upload': upload_threads,
            'packfile': config.cpu_count
        })

        self.uploader = uploader
        self.compression = config.get_compression_type()
        self.max_spool = config.max_spool
        self.audit_log = audit_log

        self.skip_existing = config.skip_existing_files

        self._progress_thread = None
        if show_progress:
            self._progress_thread = ProgressReporter(self)
            self._progress_thread.log_process_info(config.cpu_count, upload_threads, packfile_count)
            self._progress_thread.add_group('packfile', 'Packing',  packfile_count)
            self._progress_thread.add_group('upload', self.uploader.verb, upload_count + packfile_count)

    def start(self):
        super(UploadQueue, self).start()

        if self._progress_thread:
            self._progress_thread.start()

    def add_audit_log(self, task, failed=False, message=None):
        """Add audit log, if this is not a packfile task"""
        if not isinstance(task, PackfileTask):
            self.audit_log.add_log(task.fileobj.name, task.container, task.filename,
                    failed=failed, message=message)

    def complete(self, task):
        if not task.skipped:
            self.add_audit_log(task)
        super(UploadQueue, self).complete(task)

    def shutdown(self):
        # Shutdown reporting thread
        if self._progress_thread:
            self._progress_thread.shutdown()
            self._progress_thread.final_report()

        super(UploadQueue, self).shutdown()

    def suspend_reporting(self):
        if self._progress_thread:
            self._progress_thread.suspend()

    def resume_reporting(self):
        if self._progress_thread:
            self._progress_thread.resume()

    def error(self, task):
        self.add_audit_log(task, failed=True, message='Upload error')
        super(UploadQueue, self).error(task)

    def log_exception(self, job, exc_info):
        self.suspend_reporting()

        super(UploadQueue, self).log_exception(job, exc_info)

        self.resume_reporting()

    def upload(self, container, filename, fileobj):
        if self.skip_existing and self.uploader.file_exists(container, filename):
            log.debug('Skipping existing file "%s" on %s %s', filename,
                    container.container_type, container.id)
            self.skip_task(group='upload')
            self.audit_log.add_log(fileobj.name, container, filename, message='Skipped existing')
            return

        self.enqueue(UploadTask(self.uploader, self.audit_log, container, filename, fileobj=fileobj))

    def upload_file(self, container, filename, walker, path):
        if self.skip_existing and self.uploader.file_exists(container, filename):
            log.debug('Skipping existing file "%s" on %s %s', filename,
                    container.container_type, container.id)
            self.skip_task(group='upload')
            self.audit_log.add_log(path, container, filename, message='Skipped existing')
            return

        self.enqueue(UploadTask(self.uploader, self.audit_log, container, filename, walker=walker, path=path))

    def upload_packfile(self, walker, packfile_type, deid_profile, container, filename, subdir=None, paths=None):
        if self.skip_existing and self.uploader.file_exists(container, filename):
            log.debug('Skipping existing packfile "%s" on %s %s', filename,
                    container.container_type, container.id)
            self.skip_task(group='upload')
            self.skip_task(group='packfile')
            if paths:
                self.audit_log.add_log(paths[0], container, filename, message='Skipped existing')
            return

        self.enqueue(PackfileTask(self.uploader, self.audit_log, walker, packfile_type,
            deid_profile, container, filename, subdir=subdir, paths=paths,
            compression=self.compression, max_spool=self.max_spool))
