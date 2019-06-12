# encoding: utf-8

import os
import requests


class DownloadError(Exception):
    pass


def download_file(url,
                  output_dir,
                  filename=None,
                  proxies=None,
                  auth=None,
                  timeout=1.0):

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        r = requests.get(url=url,
                         auth=auth,
                         proxies=proxies,
                         timeout=timeout)

    except Exception as err:
        raise DownloadError(u'Failed to download file: {err}'.format(err=err))

    # If status code is not Success (200) then raise error with status code
    if r.status_code != 200:
        raise LookupError(r.status_code)

    if filename is None:
        filename = url.split(u'/').pop()

    full_path = u'{path}/{file}'.format(path=output_dir,
                                        file=filename)

    with open(full_path, u'wb') as handle:
        for block in r.iter_content(1024):
            handle.write(block)

    return full_path
