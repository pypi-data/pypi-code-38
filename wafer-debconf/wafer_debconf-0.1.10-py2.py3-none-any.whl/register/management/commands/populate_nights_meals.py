from django.core.management.base import BaseCommand

from register.dates import nights, meals
from register.models import AccommNight, Meal


class Command(BaseCommand):
    help = 'Create Meal and Night objects in the DB'

    def handle(self, *args, **options):
        for night in nights(orga=True):
            AccommNight.objects.get_or_create(date=night)
        for meal, date in meals(orga=True):
            Meal.objects.get_or_create(meal=meal, date=date)
