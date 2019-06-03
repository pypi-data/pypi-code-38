import re
import subprocess
import requests
import json
import os
import uuid
import hashlib
import string
from . import cnf
from . import yota



# get version number from cnf.py
version_number = cnf.version_number


def check_cache(hash_to_check, version_number):
    """Use local cache information if present."""

    # check for existence of bitly hash cashe JSON
    if os.path.isfile('hashes_i_have_seen.json'):
        with open('hashes_i_have_seen.json', 'r') as f:
            hashesIHaveSeen = json.load(f)
    else:
        hashesIHaveSeen = {}
    if hash_to_check in hashesIHaveSeen:

        return(hashesIHaveSeen[hash_to_check])
    else:
        bitly_url = 'https://bit.ly/' + hash_to_check

        #header_str = 'MediaByte ' + version_number
        #headers = {'User-Agent': header_str}
        r = requests.get(bitly_url) #, headers=headers)

        # r = requests.get(bitly_url)
        parsed_url = r.url
        hashesIHaveSeen[hash_to_check] = parsed_url
        f = open("hashes_i_have_seen.json", "w")
        json.dump(hashesIHaveSeen, f)
        f.close()

        return(parsed_url)


def youtube_time_format(seconds):
    """Takes time in seconds, returns YouTube format time code."""

    hours = int(seconds / 3600)
    seconds = seconds - (hours * 3600)
    minutes = int(seconds / 60)
    rest = seconds - minutes * 60
    final_str = ''
    if hours:
        final_str += str(hours) + 'h'
    if minutes:
        final_str += str(minutes) + 'm'
    if seconds:
        final_str += str(rest) + 's'

    return(final_str)


class Link():
    """MediaByte Bit Link object."""

    def __init__(self, bitly_hash, tags=[], title=None):

        def parse_link():

            #headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'}

            new_url = check_cache(self.bitly_hash, version_number)

            return(new_url)

        self.bitly_hash = bitly_hash

        # NB: temporary solution, random first_name for Mixtape creation
        self.first_name = uuid.uuid1().hex[:3]

        if tags:
            self.tags = tags
        else:
            self.tags = None

        if title:
            title2 = title.replace("_", " ")
            self.title = title2
            if self.tags:
                if self.tags[0] == title:
                    self.tags.pop(0)

        else:
            self.title = None

        self.url = 'https://www.bitly.com/' + self.bitly_hash

        self.link = parse_link()

        if self.tags and self.title:
            self.html = '<a href="' + \
                str(self.link) + '" title="' + " ".join(tags) + \
                '">' + str(self.title) + '</a>'

        elif self.title:
            self.html = '<a href="' + \
                str(self.link) + '">' + str(self.title) + '</a>'

        else:
            self.html = '<a href="' + \
                str(self.link) + '" title="' + str(self.tags) + '"> MyLink</a>'


        # OMM formatting
        self.omm = 'b.' + self.bitly_hash

        if self.title:
            self.omm += '.' + self.title.replace(" ", "_")
        if self.tags and self.tags[0]:
            for tag in self.tags:
                self.omm += '.' + tag
        
        # if self.omm[-1] == '.':
        #     self.omm = self.omm[:-1]  # NB: Very hacky, removing trailing '.' dot (coming from where?)

        if self.title:
            self.html = '<a href="' + self.link + '">' + self.title + '</a>'
        else:
            self.html = '<a href="' + self.link + '">MyBit</a>'


    def play(self):
        """Open sample in tab in browser."""

        subprocess.Popen(['google-chrome', self.link])

    def vlc(self):
        """Play Link in VLC Player."""

        subprocess_str = 'vlc ' + self.link
        subprocess.Popen([subprocess_str], shell=True)

    def methods(self):
        """Show methods and parameters."""

        result = []
        for item in dir(Link):
            if item.startswith('__'):
                pass
            else:
                result.append(item)

        return(result)

    def __repr__(self):
        """Defines internal print() format (internal method)."""

        if self.title == None:
            self.title = 'MyBit'
            set_temp_title = True
        else: set_temp_title = False

        tag_string = "  ("                      # build tag string
        if self.tags:
            for i, tag in enumerate(self.tags):
                tag_string += str(tag)
                if (i + 1) < len(self.tags):
                    tag_string += ', '

        tag_string += ')'

        result = ""
        if self.title:
            result = self.title + result

        if self.tags:
            tag_string = "  ("                      # build tag string
            for i, tag in enumerate(self.tags):
                tag_string += str(tag)
                if (i + 1) < len(self.tags):
                    tag_string += ', '
            tag_string += ')'
            result += tag_string

        if set_temp_title:
            self.title == None

        return(result)

    def __str__(self):
        """Returns OMM format string (internal method)."""

        return(self.omm)

    def __add__(self, value):

        new_mixtape_obj = yota.Mixtape(self)
        new_mixtape_obj += value

        return(new_mixtape_obj)

    def iframe(self, width=360, pause=False, title=False, center=True):
        """Returns IFrame format."""

        url = '<center><iframe width="360" title="YYYYY" src="XXXXX" frameborder=0 allowfullscreen></iframe></center>'
        if width != 360:
            url = url.replace('360', str(width))

        newUrl = url.replace('XXXXX', self.link)
        newUrl = newUrl.replace('YYYYY', self.title)
        if pause:
            newUrl = newUrl.replace('autoplay=1', 'autoplay=0')
        if title:
            new_title = '<center><p>' + repr(self) + '<p>'
            newUrl = newUrl.replace('<center>', new_title)
        if not center:
            newUrl = newUrl[8:-9]

        return(newUrl)

    def update(self):
        """Updates sample 'url' and 'html' parameters."""

        self.url = 'https://www.youtube.com/embed/' + \
            self.youtube_hash + '?start=0' + '&rel=0' + '&autoplay=1'

        # OMM formatting
        self.omm = 'b.' + self.bitly_hash

        if self.title:
            self.omm += '.' + self.title.replace(" ", "_")
        if self.tags and self.tags[0]:
        #if self.tags:
            for tag in self.tags:
                self.omm += '.' + tag

        self.html = '<a href="' + self.link + '">' + self.title + '</a>'


    def hash(self):
        m = hashlib.sha256()
        m.update(self.omm.encode())
        temp_hash = m.hexdigest()
        for i, char in enumerate(temp_hash):
            if char in string.ascii_letters:
                calculated_hash = temp_hash[i:i+11]
                return(calculated_hash)



class Mp3():
    """MediaByte Bit MP3 object."""

    def __init__(self, bitly_hash, tags=[], title=None, time_start=None, time_end=None):

        def parse_link():

            new_url = check_cache(self.bitly_hash, version_number)
            # r = requests.get(self.url, headers=headers)
            # new_url = r.url

            return(new_url)

        self.bitly_hash = bitly_hash

        self.first_name = uuid.uuid1().hex[:3]

        if tags:
            self.tags = tags
        else:
            self.tags = None

        if time_start:
            self.time_start = time_start
        else:
            self.time_start = None
        if time_end:
            self.time_end = time_end
        else:
            self.time_end = None

        if title:
            title2 = title.replace("_", " ")
            self.title = title2
            if self.tags:
                if self.tags[0] == title:
                    self.tags.pop(0)

        else:
            self.title = None

        self.url = 'https://www.bitly.com/' + self.bitly_hash

        self.link = parse_link()

        if self.tags and self.title:
            self.html = '<a href="' + \
                str(self.link) + '" title="' + " ".join(tags) + \
                '">' + str(self.title) + '</a>'

        elif self.title:
            self.html = '<a href="' + \
                str(self.link) + '">' + str(self.title) + '</a>'

        else:
            self.html = '<a href="' + \
                str(self.link) + '" title="' + str(self.tags) + '"> MyMp3</a>'


        # OMM formatting
        self.omm = 'b.' + self.bitly_hash
        if self.time_start:
            self.omm += '.' + str(youtube_time_format(self.time_start))

        if self.title:
            self.omm += '.' + self.title.replace(" ", "_")
        if self.tags and self.tags[0]:
        #if self.tags:
            for tag in self.tags:
                self.omm += '.' + tag
        if self.time_end:
            self.omm += '.' + str(youtube_time_format(self.time_end))

        if self.title:
            self.html = '<a href="' + self.link + '">' + self.title + '</a>'
        else:
            self.html = '<a href="' + self.link + '">MyBit</a>'

    def play(self):
        """Open sample in tab in browser."""

        subprocess.Popen(['google-chrome', self.link])

    def vlc(self):
        """Play Mp3 in VLC Player."""

        if self.time_start and self.time_end:
            parsed_link = self.link
            start_time_str = '--start-time=' + \
                str(self.time_start) + ' ' + \
                '--stop-time=' + str(self.time_end)
            subprocess_str = 'vlc ' + parsed_link + ' ' + start_time_str

            p = subprocess.Popen([subprocess_str], shell=True)

        elif self.time_start:
            parsed_link = self.link
            start_time_str = '--start-time=' + str(self.time_start)
            subprocess_str = 'vlc ' + parsed_link + ' ' + start_time_str

            p = subprocess.Popen([subprocess_str], shell=True)

        else:
            subprocess_str = 'vlc ' + parsed_link

            p = subprocess.Popen([subprocess_str], shell=True)

    def methods(self):
        """Show methods and parameters."""

        result = []
        for item in dir(Mp3):
            if item.startswith('__'):
                pass
            else:
                result.append(item)

        return(result)

    def __repr__(self):
        """Defines internal print() format (internal method)."""

        if self.title == None:
            self.title = 'MyBit'
            set_temp_title = True
        else: set_temp_title = False

        tag_string = "  ("                      # build tag string
        if self.tags:
            for i, tag in enumerate(self.tags):
                tag_string += str(tag)
                if (i + 1) < len(self.tags):
                    tag_string += ', '

        tag_string += ')'

        result = ""
        if self.title:
            result = self.title + result

        if self.tags:
            tag_string = "  ("                      # build tag string
            for i, tag in enumerate(self.tags):
                tag_string += str(tag)
                if (i + 1) < len(self.tags):
                    tag_string += ', '
            tag_string += ')'
            result += tag_string


        if set_temp_title:
            self.title == None

        return(result)

    def __str__(self):
        """Returns OMM format string (internal method)."""

        return(self.omm)

    def __add__(self, value):

        new_mixtape_obj = yota.Mixtape(self)
        new_mixtape_obj += value

        return(new_mixtape_obj)

    def __len__(self):
        """Returns clip length in seconds."""

        own_length_in_seconds = self.time_end - self.time_start

        return(own_length_in_seconds)

    def iframe(self, width=360, pause=False, title=False, center=True):
        """Returns IFrame format."""

        url = '<center><iframe width="360" title="YYYYY" src="XXXXX" frameborder=0 allowfullscreen></iframe></center>'
        if width != 360:
            url = url.replace('360', str(width))

        newUrl = url.replace('XXXXX', self.link)
        newUrl = newUrl.replace('YYYYY', self.title)
        if pause:
            newUrl = newUrl.replace('autoplay=1', 'autoplay=0')
        if title:
            new_title = '<center><p>' + repr(self) + '<p>'
            newUrl = newUrl.replace('<center>', new_title)
        if not center:
            newUrl = newUrl[8:-9]

        return(newUrl)

    def update(self):
        """Updates sample 'url' and 'html' parameters."""

        self.omm = 'b.' + self.bitly_hash

        if self.time_start:
            self.omm += '.' + youtube_time_format(self.time_start)

        if self.title:
            self.omm += '.' + self.title.replace(" ", "_")
        if self.tags and self.tags[0]:
        #if self.tags:
            for tag in self.tags:
                self.omm += '.' + tag

        if self.time_start and self.time_end:
            self.omm += '.' + youtube_time_format(self.time_end)

        self.html = '<a href="' + self.link + '">' + self.title + '</a>'

    def time(self):
        """Show sample length in 1h2m3s format."""

        own_length_in_seconds = self.time_end - self.time_start

        youtube_format_str = youtube_time_format(own_length_in_seconds)

        return youtube_format_str


    def hash(self):
        m = hashlib.sha256()
        m.update(self.omm.encode())
        temp_hash = m.hexdigest()
        for i, char in enumerate(temp_hash):
            if char in string.ascii_letters:
                calculated_hash = temp_hash[i:i+11]
                return(calculated_hash)
