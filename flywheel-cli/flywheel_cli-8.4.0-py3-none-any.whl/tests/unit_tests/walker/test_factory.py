from unittest import mock

import pytest

from flywheel_cli.walker import factory, PyFsWalker, S3Walker


@pytest.fixture
def mocked_urlparse():
    mocked_urlparse_patch = None

    def patcher(return_value):
        nonlocal mocked_urlparse_patch
        mocked_urlparse_patch = mock.patch('flywheel_cli.walker.s3_walker.urlparse')
        mocked_urlparse = mocked_urlparse_patch.start()
        mocked_urlparse.return_value = return_value
        return mocked_urlparse

    yield patcher

    if mocked_urlparse_patch is not None:
        mocked_urlparse_patch.stop()


def test_create_walker_should_request_urlparse(mocked_urlparse):
    mock_urlparse = mocked_urlparse(('s3', 'bucket', 'path'))

    factory.create_walker('s3://bucket/path/')

    mock_urlparse.assert_called_with('s3://bucket/path/')


def test_create_walker_should_create_s3_walker_instance_for_s3_scheme(mocked_urlparse):
    mocked_urlparse(('s3', 'bucket', 'path'))

    result = factory.create_walker('s3://bucket/path/')

    assert isinstance(result, S3Walker)


def test_create_walker_should_create_pyfs_walker_instance_for_os_scheme(mocked_urlparse):
    mocked_urlparse(('osfs', '/', '/'))

    result = factory.create_walker('osfs://')

    assert isinstance(result, PyFsWalker)
