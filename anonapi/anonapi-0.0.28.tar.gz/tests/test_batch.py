from io import StringIO
from pathlib import Path

import pytest

from anonapi.batch import JobBatch, BatchFolder
from anonapi.objects import RemoteAnonServer


@pytest.fixture()
def a_server():
    return RemoteAnonServer(name="temp", url="https://tempserver")


@pytest.fixture()
def a_job_batch(a_server):
    return JobBatch(job_ids=["1", "2", "3"], server=a_server)


def test_batch_persisting(a_job_batch):

    memfile = StringIO()
    a_job_batch.save(memfile)

    memfile.seek(0)
    loaded = JobBatch.load(memfile.getvalue())

    assert loaded.job_ids == a_job_batch.job_ids
    assert loaded.server.name == a_job_batch.server.name
    assert loaded.server.url == a_job_batch.server.url


def test_batch_folder(tmpdir, a_job_batch):

    # empty folder
    batch_folder = BatchFolder(path=Path(tmpdir))
    assert not batch_folder.has_batch()

    # save initial
    batch_folder.save(a_job_batch)
    assert batch_folder.has_batch()

    # should be loadable again
    loaded = BatchFolder(path=Path(tmpdir)).load()
    assert loaded.job_ids == ['1', '2', '3']
    assert str(loaded.server) == 'temp: https://tempserver'

    # add some ids and check saving
    loaded.job_ids = loaded.job_ids + ['4', '5']
    batch_folder.save(loaded)

    loaded = BatchFolder(path=Path(tmpdir)).load()
    assert loaded.job_ids == ['1', '2', '3', '4', '5']
    assert str(loaded.server) == 'temp: https://tempserver'

    batch_folder.delete_batch()
    assert not batch_folder.has_batch()
