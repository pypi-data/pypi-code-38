# Copyright (C) 2017-2018  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

from celery import current_app as app

from .loader import HgBundle20Loader, HgArchiveBundle20Loader


@app.task(name=__name__ + '.LoadMercurial')
def load_mercurial(origin_url, directory=None, visit_date=None):
    """Mercurial repository loading

    Import a mercurial tarball into swh.

    Args: see :func:`DepositLoader.load`.

    """
    loader = HgBundle20Loader()
    return loader.load(origin_url=origin_url,
                       directory=directory,
                       visit_date=visit_date)


@app.task(name=__name__ + '.LoadArchiveMercurial')
def load_archive_mercurial(origin_url, archive_path, visit_date=None):
    """Import a mercurial tarball into swh.

    Args: see :func:`DepositLoader.load`.
    """
    loader = HgArchiveBundle20Loader()
    return loader.load(origin_url=origin_url,
                       archive_path=archive_path,
                       visit_date=visit_date)
