from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from system.utils import tools
from urllib import parse


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('url', type=str)
        parser.add_argument('title', type=str)

    def handle(self, *args, **options):
        my_url = options.get('url')
        title = options.get('title')
        url_info = parse.urlparse(my_url)
        site = Site.objects.filter(domain=url_info.netloc).get()
        ret = tools.push_baidu(my_url, title, site)
        print('push url to baidu: %s remain: %s' % (str(ret['success']), str(ret['remain'])))
