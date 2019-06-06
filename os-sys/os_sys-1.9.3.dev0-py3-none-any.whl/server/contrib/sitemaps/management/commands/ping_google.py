from server.contrib.sitemaps import ping_google
from server.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Ping Google with an updated sitemap, pass optional url of sitemap"

    def add_arguments(self, parser):
        parser.add_argument('sitemap_url', nargs='?', default=None)

    def handle(self, *args, **options):
        ping_google(sitemap_url=options['sitemap_url'])
