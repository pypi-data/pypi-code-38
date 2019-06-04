import requests

from django.core.management.base import BaseCommand

from wafer.talks.models import Talk


class Command(BaseCommand):
    help = 'Import published talk videos'

    def handle(self, *args, **options):
        released = requests.get('https://sreview.debian.net/released').json()
        for video in released:
            id_ = int(video['waferurl'].split('/')[2])
            url = video['publicurl']
            talk = Talk.objects.get(pk=id_)
            tu, created = talk.urls.update_or_create(
                description='Video', defaults={'url': url})

            if created:
                print('Set URL for {}'.format(talk.title))
