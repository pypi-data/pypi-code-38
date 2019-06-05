import sys
import re
import eyed3

from .. import path
from ..utils import obj2xml


def do():


    print("Modify a folder of mp3 files' ID3 based on file names")

    p = path(sys.argv[1] if len(sys.argv) > 1 else '.')

    print("Folder: {}".format(p))

    files = []

    for f, name in p.filter(filetype='mp3', recursive=False):

        x = re.split(' - ', name)

        album, artist, song = *((3-len(x)) * (None, )), *x

        print(album, artist, song)

        af = eyed3.load(f)
        print(af.tag)
        # af.tag.remove(f)

        # print(af.tag.artist, af.tag.album, af.tag.title)

    print("{} altogether".format(len(files)))


    # audiofile = eyed3.load("song.mp3")
    # audiofile.tag.artist = u"Integrity"
    # audiofile.tag.album = u"Humanity Is The Devil"
    # audiofile.tag.album_artist = u"Integrity"
    # audiofile.tag.title = u"Hollow"
    # audiofile.tag.track_num = 2

    # audiofile.tag.save()

    # audiofile.tag.remove()







if __name__ == '__main__': do()