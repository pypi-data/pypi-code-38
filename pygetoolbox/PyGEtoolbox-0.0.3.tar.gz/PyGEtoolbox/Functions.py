"""
A collection of functions

- progress bar for downloading datasets (chunk_report, chunk_read), based on solution from http://stackoverflow.com/questions/5783517/downloading-progress-bar-urllib2-python

"""
import urllib2
import sys


def chunk_report(bytes_so_far, chunk_size, total_size):
    percent = float(bytes_so_far) / total_size
    percent = round(percent * 100, 2)
    sys.stdout.write("Downloaded %d of %d bytes (%0.2f%%)\r" %
                     (bytes_so_far, total_size, percent))

    if bytes_so_far >= total_size:
        sys.stdout.write('\n')


def chunk_read(response, chunk_size=8192, report=None):
    total_size = response.info().getheader('Content-Length').strip()
    total_size = int(total_size)
    bytes_so_far = 0
    data = []

    while True:
        chunk = response.read(chunk_size)
        bytes_so_far += len(chunk)

        if not chunk:
            break

        data += chunk
        if report:
            report(bytes_so_far, chunk_size, total_size)

    return "".join(data)
