import json
import logging
import urllib.request
from datetime import datetime
from json import JSONDecodeError

from pysmoothstreams import Feed, Quality, Server, Protocol, Service
from pysmoothstreams.exceptions import InvalidQuality, InvalidServer, InvalidProtocol


class Guide:
    def __init__(self, feed=Feed.SMOOTHSTREAMS):
        self.channels = []
        self.expires = None

        self.url = feed.value if isinstance(feed, Feed) else feed
        self._fetch_channels()

    def _parse_expiration_string(self, expiration):
        return datetime.strptime(expiration, '%a, %d %b %Y %H:%M:%S %Z')

    def _fetch_channels(self, force=False):

        if self.expires is None or datetime.now() > self.expires or force:

            with urllib.request.urlopen(self.url) as response:
                self.expires = self._parse_expiration_string(response.info()['Expires'])
                logging.debug(f'Guide info set to expire in {self.expires}')

                try:
                    as_json = json.loads(response.read())
                    logging.debug(f'Retrieved {len(as_json)} channels from feed.')
                    self.channels = []

                    for key, value in as_json.items():
                        c = {'number': value['channel_id'],
                             'name': value['name'],
                             'icon': value['img']}
                        logging.debug(f'Created channel: number {c["number"]}, name {c["name"]}, icon {c["icon"]}')
                        self.channels.append(c)

                except JSONDecodeError as e:
                    logging.critical(f'Feed at {self.url} did not return valid JSON! Channel list is empty!')

            logging.debug(f'Fetched {len(self.channels)} channels.')

        else:
            logging.debug('Channels are not stale or fetched was not forced.')

    def _build_stream_url(self, server, channel_number, auth_sign, quality=Quality.HD, protocol=Protocol.HLS):
        # https://dEU.smoothstreams.tv:443/view247/ch01q1.stream/playlist.m3u8?wmsAuthSign=abc1234
        # https://dEU.smoothstreams.tv:443/view247/ch01q1.stream/mpeg.2ts?wmsAuthSign=abc1234
        port = '443'
        playlist = 'playlist.m3u8'

        if protocol == Protocol.RTMP:
            if auth_sign.service == Service.LIVE247:
                port = '3625'
            if auth_sign.service == Service.STARSTREAMS:
                port = '3665'
            if auth_sign.service == Service.STREAMTVNOW:
                port = '3615'
            if auth_sign.service == Service.MMATV:
                port = '3635'

        if protocol == Protocol.MPEG:
            playlist = 'mpeg.2ts'

        c = str(channel_number).zfill(2)
        stream_url = f'{protocol}://{server}:{port}/{auth_sign.service.value}/ch{c}q{quality}.stream/{playlist}?wmsAuthSign={auth_sign.fetch_hash()}'
        return stream_url

    def generate_streams(self, server, quality, auth_sign, protocol=Protocol.HLS):
        streams = []

        if not isinstance(server, Server):
            raise InvalidServer(f'{server} is not a valid server!')

        if not isinstance(quality, Quality):
            raise InvalidQuality(f'{quality} is not a valid quality!')

        if not isinstance(protocol, Protocol):
            raise InvalidProtocol(f'{protocol} is not a valid protocol!')

        if self.channels:
            for c in self.channels:
                stream = c.copy()
                stream['url'] = self._build_stream_url(server, c['number'], auth_sign, quality, protocol)

                streams.append(stream)

            logging.info(f'Returning {len(streams)} streams.')
            return streams
