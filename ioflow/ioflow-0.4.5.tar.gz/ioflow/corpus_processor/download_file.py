import os
import tempfile

import requests


def download_file(url, filename=None, **kwargs):
    """
    code learned from https://stackoverflow.com/a/16696317/1979770
    """
    # create a temp file if filename is not given
    if not filename:
        filename = os.path.join(tempfile.mkdtemp(), 'corpus.data')

    # NOTE the stream=True parameter below
    with requests.get(url, stream=True, **kwargs) as r:
        r.raise_for_status()
        with open(filename, 'wb') as f:
            chunk_size = 1 << 10  # e.g. 1024
            for chunk in r.iter_content(chunk_size=chunk_size):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
                    # f.flush()
    return filename


if __name__ == "__main__":
    # download_file("http://10.43.13.20:25005/hdfs/download", filename='download.txt', json={"trainId": "5d01cc3bb775fa16367a2f85"})
    result = download_file("http://10.43.10.17:25005/hdfs/download", params={"trainId": "5d01cc3bb775fa16367a2f85"})

    print(result)

