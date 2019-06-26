# -*- coding: utf-8 -*-
from missinglink.sdk import PackageProvider


def create_http_session():
    import requests

    # kernel_version is always the most up to date as it get auto updated
    # while the sdk version will get updated only after rerun
    kernel_version = PackageProvider.get_dist_version('missinglink-kernel')

    session = requests.Session()

    session.headers.update({'User-Agent': 'ml-sdk/{}'.format(kernel_version)})

    return session
