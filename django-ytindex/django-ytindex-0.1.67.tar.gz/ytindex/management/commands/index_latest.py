from urllib import request
from xml.etree import ElementTree

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from ytindex.indexing import Index
from ytindex.indexing.downloader import YTCaptionDownloader, YTCaptionNotFoundException

class Command(BaseCommand):
    help = 'Index the latest videos from a channel'

    def add_arguments(self, parser):
        parser.add_argument('index', nargs='+', type=str)

    def handle(self, *args, **options):

        def index_video(ytid, idx, ls=12):
            downloader = YTCaptionDownloader(ytid, line_size=ls)
            idx.index_object(downloader.as_dict())

        for index in options['index']:
            idx_settings = settings.YTCI_SETTINGS[index]
            idx = Index(**idx_settings['elastic'])
            channel_id = idx_settings['channel_id']

            r = request.urlopen('https://www.youtube.com/feeds/videos.xml?channel_id=%s'%channel_id)
            if r.status == 200:
                et = ElementTree.fromstring(r.read())
                ns = {'xmlns':'http://www.w3.org/2005/Atom'}
                xpath = './xmlns:entry/xmlns:id'
                video_ids = [id.text.split(':')[-1] for id in et.findall( xpath, namespaces=ns )]
                for video_id in video_ids:
                    try:
                        print('Indexing::', video_id)
                        index_video(video_id, idx, ls=idx_settings.get('line_size', 12))
                    except YTCaptionNotFoundException as e:
                        print(e)
                    except Exception as e:
                        print('Most unexpected!!!', e)
