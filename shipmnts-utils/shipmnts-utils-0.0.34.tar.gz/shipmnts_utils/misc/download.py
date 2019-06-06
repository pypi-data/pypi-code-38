import os

import requests


def serve_request_write_content(url, destination):
    r = requests.get(url, allow_redirects=True)
    open(destination + "/" + url.split("/")[-1], "wb").write(r.content)


def download_file(source, destination, multiple=False):
    os.makedirs(destination, exist_ok=True)
    if multiple:
        for url in source:
            serve_request_write_content(url=url, destination=destination)
    else:
        serve_request_write_content(url=source, destination=destination)
