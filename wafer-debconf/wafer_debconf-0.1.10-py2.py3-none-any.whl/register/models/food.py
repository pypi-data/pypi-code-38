from collections import OrderedDict

from django.conf import settings
from django.db import models
from django.utils.functional import cached_property

from register.models.attendee import Attendee


class Meal(models.Model):
    MEALS = OrderedDict((
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
    ))

    date = models.DateField(db_index=True)
    meal = models.CharField(max_length=16)

    @cached_property
    def form_name(self):
        return '{}_{}'.format(self.meal, self.date.isoformat())

    @cached_property
    def conference_dinner(self):
        return (self.meal == 'dinner'
            and self.date == settings.DEBCONF_CONFERENCE_DINNER_DAY)

    def __str__(self):
        return '{}: {}'.format(self.date.isoformat(), self.meal)

    class Meta:
        ordering = ['date']
        unique_together = ('date', 'meal')


class Food(models.Model):
    DIETS = OrderedDict((
        ('', 'I will be happy to eat whatever is provided'),
        ('vegetarian', "I am lacto-ovo vegetarian, don't provide "
                       "meat/fish for me"),
        ('vegan', "I am strict vegetarian (vegan), don't provide any "
                  "animal products for me"),
        ('gluten_free', 'I require gluten-free food'),
        ('other', 'Other, described below'),
    ))

    attendee = models.OneToOneField(Attendee, related_name='food',
                                    on_delete=models.CASCADE)

    meals = models.ManyToManyField(Meal)
    diet = models.CharField(max_length=16, blank=True)
    special_diet = models.TextField(blank=True)

    def __str__(self):
        return 'Attendee <{}>'.format(self.attendee.user.username)

    @cached_property
    def meals_by_day(self):
        meal_order = list(Meal.MEALS.keys())
        meals = sorted(
            self.meals.all(),
            key=lambda meal: (meal.date, meal_order.index(meal.meal)))

        by_day = OrderedDict()
        for meal in meals:
            by_day.setdefault(meal.date, []).append(meal)
        return by_day
