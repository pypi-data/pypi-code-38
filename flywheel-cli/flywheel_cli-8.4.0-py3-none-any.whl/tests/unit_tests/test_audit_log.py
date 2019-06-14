import csv
import os
import tempfile
from unittest import mock

import pytest

from flywheel_cli.importers.container_factory import ContainerNode
from flywheel_cli.importers.audit_log import AuditLog


@pytest.fixture(scope='session')
def audit_path():
    file_path = tempfile.mktemp()

    yield file_path

    if os.path.exists(file_path):
        os.remove(file_path)


def test_audit_log_constructor_no_path_is_valid(audit_path):
    audit_log = AuditLog(None)
    assert audit_log.path is None


def test_audit_log_constructor_with_path_creates_file(audit_path):
    # Audit log created with path should write the header
    audit_log = AuditLog(audit_path)
    assert audit_log.path == audit_path

    assert os.path.isfile(audit_path)

    with open(audit_path, 'r') as f:
        reader = csv.reader(f)

        rows = list(iter(reader))
        assert len(rows) == 1
        assert rows[0] == ['Source Path', 'Flywheel Path', 'Failed', 'Message']

    # Audit log created 2nd time with path should NOT write the header
    audit_log = AuditLog(audit_path)

    with open(audit_path, 'r') as f:
        reader = csv.reader(f)
        rows = list(iter(reader))
        assert len(rows) == 1
        assert rows[0] == ['Source Path', 'Flywheel Path', 'Failed', 'Message']


def test_audit_log_get_container_resolver_path():
    audit_log = AuditLog(None)

    assert audit_log.get_container_resolver_path(None) == ''

    root = ContainerNode('root')
    assert audit_log.get_container_resolver_path(root) == ''

    group = ContainerNode('group', cid='groupid', parent=root)
    assert audit_log.get_container_resolver_path(group) == 'groupid'

    project = ContainerNode('project', label='The Project', parent=group)
    assert audit_log.get_container_resolver_path(project, file_name='file.txt') == 'groupid/The Project/files/file.txt'


def test_audit_log_add_log(audit_path):
    audit_log = AuditLog(audit_path)

    root = ContainerNode('root')
    group = ContainerNode('group', cid='groupid', parent=root)


    audit_log.add_log('/src/path', group, 'file1.txt')

    with open(audit_path, 'r') as f:
        reader = csv.reader(f)
        rows = list(iter(reader))
        assert len(rows) == 2

        assert rows[1] == ['/src/path', 'groupid/files/file1.txt', 'false', '']


def test_audit_log_finalize_noop(audit_path):
    container_factory = mock.MagicMock()

    audit_log = AuditLog(None)
    audit_log.finalize(container_factory)  # no-op


def test_audit_log_finalize_no_project(audit_path):
    container_factory = mock.MagicMock()

    root = ContainerNode('root')
    group = ContainerNode('group', cid='groupid', parent=root)
    project = ContainerNode('project', label='The Project', parent=group)

    audit_log = AuditLog(audit_path)
    with mock.patch('flywheel_cli.importers.audit_log.log') as patched_log:
        container_factory.get_first_project.return_value = None
        audit_log.finalize(container_factory)

        container_factory.get_first_project.assert_called()
        patched_log.info.assert_called_with('No project found for import, skipping audit-log upload')


def test_audit_log_finalize_with_upload_error(audit_path):
    container_factory = mock.MagicMock()

    root = ContainerNode('root')
    group = ContainerNode('group', cid='groupid', parent=root)
    project = ContainerNode('project', label='The Project', parent=group)

    audit_log = AuditLog(audit_path)
    with mock.patch('flywheel_cli.importers.audit_log.log') as patched_log:
        container_factory.get_first_project.return_value = project

        container_factory.resolver.upload.side_effect = RuntimeError('Runtime error occurred')

        audit_log.finalize(container_factory)

        container_factory.resolver.upload.assert_called()
        container_factory.get_first_project.assert_called()
        patched_log.error.assert_called_with('Error uploading audit-log', exc_info=True)

        assert os.path.isfile(audit_path)

def test_audit_log_finalize_success(audit_path):
    container_factory = mock.MagicMock()

    root = ContainerNode('root')
    group = ContainerNode('group', cid='groupid', parent=root)
    project = ContainerNode('project', label='The Project', parent=group)

    audit_log = AuditLog(audit_path)
    with mock.patch('flywheel_cli.importers.audit_log.log') as patched_log:
        container_factory.get_first_project.return_value = project

        audit_log.finalize(container_factory)

        container_factory.resolver.upload.assert_called()
        container_factory.get_first_project.assert_called()

        # File did not get deleted
        assert os.path.isfile(audit_path)

