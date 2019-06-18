
from dataclasses import dataclass
from thisamericanlife.endpoints import get_full_url_template
from thisamericanlife.html.transcript import TranscriptHtml


@dataclass
class EpisodeMeta(object):
    raw_title: str
    title: str = None
    number: int = None

    @staticmethod
    def from_raw(raw_string):
        episode_title, episode_number = None, None
        if raw_string:
            parsed = raw_string.split(':')
            episode_title = parsed[-1].strip()
            try:
                episode_number = int(parsed[0])
            except:
                episode_number = None

        return EpisodeMeta(raw_string, episode_title, episode_number)


class TranscriptInstance(object):
    @staticmethod
    def from_html(html):
        return TranscriptInstance(body_json=TranscriptHtml(html).to_json())

    def __init__(self, body_json=None):
        self.body_json = body_json
        self.episode_meta_info = EpisodeMeta.from_raw(self.body_json['episode_title'])
        self.transcript = self.body_json['transcript']


class Transcripts(object):
    def __init__(self, http_client=None):
        self.http_client = http_client
        self._endpoint = get_full_url_template('transcript')

    def get(self, episode_number):
        resp = self.http_client.get(self._endpoint.format(episode_number=episode_number))

        return TranscriptInstance.from_html(resp.content)
