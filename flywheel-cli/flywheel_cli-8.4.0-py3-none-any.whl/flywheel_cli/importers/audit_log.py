"""Provides audit logging class"""
import csv
import logging
import os

log = logging.getLogger(__name__)

class AuditLog(object):
    def __init__(self, audit_log_path):
        self.headers = ['Source Path', 'Flywheel Path', 'Failed', 'Message']
        self.path = audit_log_path

        if self.path and not os.path.exists(self.path):
            with open(self.path, 'w') as log_file:
                csv_writer = csv.DictWriter(log_file, fieldnames=self.headers)
                csv_writer.writeheader()

    def log_root_dir(self, rootdir):
        if self.path:
            self._write_entry(src_path=rootdir, message='Begin import scan')

    def add_log(self, src_path, container, file_name, failed=False, message=None):
        if self.path:
            resolver_path = self.get_container_resolver_path(container, file_name)
            self._write_entry(src_path=src_path, flywheel_path=resolver_path,
                failed='true' if failed else 'false', message=message or '')

    def _write_entry(self, src_path='', flywheel_path='', failed='', message=''):
        with open(self.path, 'a') as log_file:
            csv_writer = csv.DictWriter(log_file, fieldnames=self.headers)
            csv_writer.writerow({
                'Source Path': src_path,
                'Flywheel Path': flywheel_path,
                'Failed': failed,
                'Message': message
            })

    def get_container_resolver_path(self, container, file_name=None):
        path = []
        if container is None:
            return ''
        while container.container_type != 'root':
            if container.container_type == 'group':
                path = [container.id] + path
            else:
                path = [container.label] + path
            container = container.parent
        if file_name is not None:
            path += ['files', file_name]
        return '/'.join(path)

    def finalize(self, container_factory):
        if not self.path:
            return

        # Upload the audit log to the target project
        project = container_factory.get_first_project()
        if not project:
            log.info('No project found for import, skipping audit-log upload')
            return

        if not hasattr(container_factory.resolver, 'upload'):
            log.warn('Cannot upload audit-log -- no upload function available')
            return

        try:
            log_name = os.path.basename(self.path)
            with open(self.path, 'rb') as f:
                container_factory.resolver.upload(project, log_name, f)
        except:
            log.error('Error uploading audit-log', exc_info=True)
        else:
            print('%s uploaded to the "%s" project.' % (
                log_name, project.label))
