"""Provides a scanner that will group files together under a common prefix"""
import copy

from .abstract_scanner import AbstractScanner


class SlurpScanner(AbstractScanner):
    """SlurpScanner groups files together by a common prefix.

    This works by looking at the first slash (or if there is no slash, the first dot) in
    each file path, and using that as the acquisition label.
    """
    def __init__(self, config):
        """Class that handles generic acquisition slurping"""
        super(SlurpScanner, self).__init__(config)

    def discover(self, walker, context, container_factory, path_prefix=None, audit_log=None):
        # Discover files first
        files = list(sorted(walker.files(subdir=path_prefix)))

        prefix_len = len(path_prefix or '')

        current_prefix = None
        current_files = []

        for path in files:
            path = path.lstrip('/')

            prefix = SlurpScanner._get_prefix(path[prefix_len:])
            if prefix == current_prefix:
                current_files.append(path)
            else:
                self._add_acquisition(container_factory, context, current_prefix, current_files)

                current_prefix = prefix
                current_files = [path]

        self._add_acquisition(container_factory, context, current_prefix, current_files)

    @staticmethod
    def _get_prefix(path):
        """Get the appropriate prefix for the given file"""
        try:
            idx = path.rindex('/')
        except ValueError:
            try:
                idx = path.index('.')
            except ValueError:
                idx = len(path)

        return path[:idx].strip('/').replace('/', '_')

    def _add_acquisition(self, container_factory, context, label, files):
        if not label or not files:
            return

        acquisition_context = copy.deepcopy(context)
        acquisition_context.setdefault('acquisition', {})['label'] = label

        container = container_factory.resolve(acquisition_context)
        container.files.extend(files)
