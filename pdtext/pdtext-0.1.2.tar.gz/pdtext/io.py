from time import sleep
from .slugify import slugify
import requests
import os


def locate(url, directory = 'html'):
    '''Create file name and place in directory'''

    # check directory
    if os.path.isdir(directory) == False:
        print("HTML directory does not exist. Being created.")
        os.mkdir(directory)

    file_name = slugify(url)
    location = os.path.join(directory, file_name)
    return location

def open_html(url, directory = 'html'):
    """Attempt to open a file based on the url."""
    location = locate(url, directory)

    with open(location, "r") as infile:
        html = infile.read()

    return html

def get_html(url, directory, pause):
    """Download & save html text using the url to create the filename."""

    sleep(pause)
    r = requests.get(url)
    html = r.text

    location = locate(url, directory = directory)

    with open(location, "w") as outfile:
        outfile.write(html)

    return html


def retrieve_html(url, directory = 'html', pause = 1):
    '''Attempt to load html file locally. If that doesn't work, download and save it first.'''
    try:
        return open_html(url, directory)
    except:
        return get_html(url, directory, pause)
