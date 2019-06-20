from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.detail import DetailView
from front_desk.views import CheckInPermissionMixin
from register.models import Accomm, Food, Meal
from django.contrib.auth.models import User

from register.dates import meals as dc_meals


def attendee_context(context, attendee):
    dates = sorted(set(date for meal, date in dc_meals(orga=True)))
    meal_labels = ['Breakfast', 'Lunch', 'Dinner']

    try:
        food = attendee.food
    except Food.DoesNotExist:
        food = None

    meals = []
    for meal, meal_label in Meal.MEALS.items():
        cur_meal = []
        meal_dates = []

        if food != None:
            meal_dates = [entry.date
                          for entry in food.meals.filter(meal=meal)]

        for d in dates:
            cur_meal.append((d, d in meal_dates))
        meals.append((meal_label, cur_meal))

    try:
        accomm = attendee.accomm
    except Accomm.DoesNotExist:
        accomm = None

    nights = []
    night_dates = []
    if accomm != None:
        night_dates = [entry.date
                      for entry in accomm.nights.all()]

    for d in dates:
        nights.append((d, d in night_dates))

    context.update({
        'dates': dates,
        'meal_labels': meal_labels,
        'meals': meals,
        'nights': nights,
    })
    return context


class OwnBadge(LoginRequiredMixin, DetailView):
    template_name = 'badges/single_badge.html'

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        attendee = self.object.attendee

        return attendee_context(context, attendee)


class CheckInBadgeView(CheckInPermissionMixin, DetailView):
    template_name = 'badges/single_badge.html'

    model = User
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        attendee = self.object.attendee

        return attendee_context(context, attendee)
