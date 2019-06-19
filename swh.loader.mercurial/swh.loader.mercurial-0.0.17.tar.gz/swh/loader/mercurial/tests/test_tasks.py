# Copyright (C) 2018  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

from unittest.mock import patch


@patch('swh.loader.mercurial.loader.HgBundle20Loader.load')
def test_loader(mock_loader, swh_app, celery_session_worker):
    mock_loader.return_value = {'status': 'eventful'}

    res = swh_app.send_task(
        'swh.loader.mercurial.tasks.LoadMercurial',
        kwargs=dict(origin_url='origin_url', directory='/some/repo',
                    visit_date='now'))
    assert res
    res.wait()
    assert res.successful()

    assert res.result == {'status': 'eventful'}
    mock_loader.assert_called_once_with(
        origin_url='origin_url', visit_date='now', directory='/some/repo')


@patch('swh.loader.mercurial.loader.HgArchiveBundle20Loader.load')
def test_archive_loader(mock_loader, swh_app, celery_session_worker):
    mock_loader.return_value = {'status': 'uneventful'}

    res = swh_app.send_task(
        'swh.loader.mercurial.tasks.LoadArchiveMercurial',
        ('another_url', '/some/tar.tgz', 'now'))
    assert res
    res.wait()
    assert res.successful()

    assert res.result == {'status': 'uneventful'}
    mock_loader.assert_called_once_with(
        origin_url='another_url',
        archive_path='/some/tar.tgz',
        visit_date='now')
