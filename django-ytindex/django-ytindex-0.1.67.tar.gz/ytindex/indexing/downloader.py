import re
from datetime import datetime, timedelta

# It might make sense to use the official API down the line
# For now this was quicker than getting a key, etc.
from pytube import YouTube

class YTCaptionException(Exception):
    pass
class YTCaptionNotFoundException(YTCaptionException):
    pass

class YTCaptionDownloader:
    # CaptionDownloader downloads video info and auto captions for a given
    # Youtube video and makes it available as a dict.

    def __init__(self, yt_id, line_size=20, lang='en'):
        # yt_id: id of the Youtube video
        # line_size: how many individual caption lines should be chunked together
        # lang: desired subtitle language. (hardly anything but en makes sense right now but who knows)
         self.yt_id = yt_id
         self._ls = line_size
         self._lang = lang
         self._captions = None
         self.__ud = None
         self.__create_yt()

    def __create_yt(self):
        ## pytube.YouTube sometimes fails on __init__ idkw
        MAX_RETRIES = 3
        retries = 0
        while retries < MAX_RETRIES:
            try:
                self._yt = YouTube('https://www.youtube.com/watch?v=%s'%self.yt_id)
                return
            except Exception as e:
                retries += 1
                print('pytube.YouTube failed on init %i tries left'%(MAX_RETRIES-retries))
                if retries >= MAX_RETRIES:
                    print('Catastrophic: pytube.Youtube failed on init %i times. Giving up.'%MAX_RETRIES)
                    raise e

    @classmethod
    def timecode2seconds(cls, timecode):
        # SRT timecodes are HH:MM:SS, we want seconds
        tr = re.compile('(?P<hours>\d{2}):(?P<minutes>\d{2}):(?P<seconds>\d{2})')
        td = timedelta( **dict( ((k,int(v)) for k, v in tr.match(timecode).groupdict().items()) ) )
        return td.total_seconds()

    @classmethod
    def compact(cls, lines, line_size=5 ):
        # Captions can be super atomic, group them together.

        def _merge_lines( lines ):
            # Merge a list of lines into one
            start = lines[0]['start']
            end = lines[-1]['end']
            content = ' '.join([l['content'] for l in lines])
            return {'start': start, 'end': end, 'content': content}

        i = 0
        new_lines = []
        while i < len(lines)-line_size:
            new_lines.append(_merge_lines(lines[i:i+line_size]))
            i += line_size

        # Merge any remaining lines
        new_lines.append(_merge_lines(lines[i:]))
        return new_lines

    def _get_captions(self, lang='en', line_size=20 ):
        c = self._yt.captions.get_by_language_code(lang)
        if not c: raise YTCaptionNotFoundException('No captions found for %s'%self.id)
        s = c.generate_srt_captions()
        s = re.sub( '<[^>]*>', '', s ) # Remove styling
        lines = s.split('\n\n') # Split the SRT sections

        # Parse SRT
        def _parse_srt_line(line):
            index, time, content = line.split('\n')
            start, end = time.split(' --> ')
            start = self.timecode2seconds(start)
            end = self.timecode2seconds(end)
            return {'start':start, 'end':end, 'content':content}

        lines = [_parse_srt_line(line) for line in lines]
        return self.compact(lines, line_size=line_size)

    # Properties
    @property
    def id(self):
        return self._yt.video_id
    @property
    def author(self):
        return self._yt.player_config_args['author']
    @property
    def title(self):
        return self._yt.title
    @property
    def description(self):
        return self._yt.description
    @property
    def thumbnail(self):
        try:
            return self._yt.thumbnail_url
        except KeyError:
            return None
        
    @property
    def upload_date(self):
        if self.__ud is None:
            reg = r'(?isx)<meta(?=[^>]+(?:itemprop|name|property|id|http-equiv)=(["\']?)datePublished\1)[^>]+?content=(["\'])(?P<upload_date>.*?)\2'
            m = re.search(reg, self._yt.watch_html)
            if m:
                date = m.group('upload_date')
                self.__ud = datetime.strptime(date, '%Y-%m-%d')
        return self.__ud
    @property
    def captions(self):
        if self._captions is None:
            self._captions = self._get_captions( lang=self._lang, line_size=self._ls)
        return self._captions
    @property
    def url(self):
        return self._yt.watch_url
    def jump_url(self, seconds):
        return '%s&t=%ss'%(self.url, seconds)

    def as_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'thumbnail': self.thumbnail,
            'url': self.url,
            'upload_date': self.upload_date,
            'captions': self.captions
        }
