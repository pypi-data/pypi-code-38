import json
from abc import ABC

from libmediainfo_cffi import MediaInfo

from .commons import Caption
from ..commons import ParseMode
from ...utils import MultipartEncoder, random_string


class File(ABC):
    file_type = None
    attributes = []
    cache = {}

    def __init__(self, file, is_path=True):
        """Generic File class, supports automatic metadata reading via MediaInfo bindings and caching

        :param file: a path (default) or a valid string recognizable by the Telegram endpoint (an url or a file id)
        :param is_path: whether file is a path (default) or anything else
        """

        # cache is a dict {file_path: file_id} and should be updated with the trigger callback
        self.args = {}
        self.file = file
        self.is_path = is_path

        # if we received a path we first check we have the file inside the cache dict
        # if we do then we treat this as a File with "is_path" set to false and we use the file_id we've found as
        # else we store encode the file as multipart/form-data
        if is_path is True:
            file_id = self.cache.get(self.file)
            if file_id is not None:
                self.method = 'GET'
                self.value = file_id
            else:
                self.method = 'POST'
                self.value = [MultipartEncoder.encode_file(self.file_type, self.file)]
        else:
            self.method = 'GET'
            self.value = self.file

    def read_metadata(self, json_lib=None):
        """Read metadata from the file (if it's a file)"""

        if self.method == 'GET':
            return self

        data = MediaInfo.read_metadata(self.file, Inform='JSON')

        if json_lib is None:
            _json = json
        else:
            _json = json_lib

        data = _json.loads(data)
        data_dict = {}

        # redrder the data to avoid O(tracks number) behavior while checking for tracks of a given type
        # also we use only the first track found, you can override this method if this doesn't work for you
        for track in data['media']['track']:
            _type = track['@type']

            if data_dict.get(_type) is None:
                data_dict[_type] = track

        for attribute, _type, key in self.attributes:
            if callable(_type):
                attribute_value = _type(data)
            else:
                track = data_dict.get(_type)
                if track is None:
                    continue

                attribute_value = track.get(key)

            if attribute_value is None:
                continue

            self.args[attribute] = attribute_value

        return self

    def with_cache(self):
        """Check if a file_id can be used instead of a multipart/form-data request"""

        if self.method == 'GET':
            return self

        if not hasattr(self, 'use_cache'):
            self.use_cache = True
            return self

        file_id = self.cache.get(self.file)

        if file_id is not None:
            self.method = 'GET'
            self.value = file_id
            self.is_path = False

        return self

    @staticmethod
    def _get_file_id(response):
        """If the telegram response is (for example) an array or a map, here you can return the correct entry to the
        update_cache function
        """

        return response

    def update_cache(self, response, index=None):
        """Updates the object cache with the file ids"""

        file_id = self.cache.get(self.file)
        if file_id is None:
            response = response['result']
            if index is not None:
                response = response[index][self.file_type]
            else:
                response = response[self.file_type]

            self.cache[self.file] = self._get_file_id(response)['file_id']


class ToInputMedia:
    media_types = ['photo', 'video']

    def to_input_media(self):
        # mixin to be used with the File class, look at it for unresolved references

        serialized = {
            'type': self.file_type,
            **self.args
        }

        if self.method == 'POST':
            files = []
            for file in self.value:
                field_name = random_string()  # avoid conflicts
                if file[0] in self.media_types:
                    serialized['media'] = f'attach://{field_name}'
                else:
                    serialized[file[0]] = f'attach://{field_name}'
                files.append((field_name, file[1], file[2], file[3]))
            return serialized, files
        else:
            serialized['media'] = self.value
            return serialized, None


class Thumb:
    def thumb(self, thumb):
        # thumb must be a path
        if self.method == 'POST':
            self.value.append(MultipartEncoder.encode_file('thumb', thumb))
        return self


class Photo(File, Caption, ParseMode, ToInputMedia):
    file_type = 'photo'

    @staticmethod
    def _get_file_id(response):
        return response[-1]


class Audio(File, Caption, ParseMode, Thumb, ToInputMedia):
    file_type = 'audio'
    attributes = [
        ('duration', 'General', 'Duration'),
        ('performer', 'General', 'Performer'),
        ('title', 'General', 'Track')
    ]

    def duration(self, duration):
        self.args['duration'] = duration
        return self

    def performer(self, performer):
        self.args['performer'] = performer
        return self

    def title(self, title):
        self.args['title'] = title
        return self


class Document(File, Caption, ParseMode, Thumb, ToInputMedia):
    file_type = 'document'


class Video(File, Caption, ParseMode, Thumb, ToInputMedia):
    file_type = 'video'
    attributes = [
        ('duration', 'General', 'Duration'),
        ('width', 'Video', 'Width'),
        ('height', 'Video', 'Height')
    ]

    def supports_streaming(self):
        self.args['supports_streaming'] = True
        return self

    def duration(self, duration):
        self.args['duration'] = duration
        return self

    def width(self, width):
        self.args['width'] = width
        return self

    def height(self, height):
        self.args['height'] = height
        return self


class Animation(File, Caption, ParseMode, Thumb, ToInputMedia):
    file_type = 'animation'
    attributes = [
        ('duration', 'General', 'Duration'),
        ('width', 'Video', 'Width'),
        ('height', 'Video', 'Height')
    ]

    def duration(self, duration):
        self.args['duration'] = duration
        return self

    def width(self, width):
        self.args['width'] = width
        return self

    def height(self, height):
        self.args['height'] = height
        return self


class Voice(File, Caption, ParseMode):
    file_type = 'voice'
    attributes = [
        ('duration', 'General', 'Duration')
    ]

    def duration(self, duration):
        self.args['duration'] = duration
        return self


def get_length(data_dict):
    track = data_dict.get('Video')
    if track is None:
        return

    width = track.get('Width')
    height = track.get('Height')
    if width < height:
        return width
    else:
        return height


class VideoNote(File, Thumb):
    file_type = 'video_note'
    attributes = [
        ('duration', 'General', 'Duration'),
        ('length', get_length, None),
    ]

    def duration(self, duration):
        self.args['duration'] = duration
        return self

    def length(self, length):
        self.args['length'] = length
        return self
