from django.conf import settings
from crispy_forms.layout import Field

from register.dates import conference_dinner_meal, parse_date


class MealSelectionField(Field):
    template = 'register/fields/meals.html'

    def render(self, form, form_style, context, **kwargs):
        field = self.fields[0]
        bound_field = form[field]

        by_day = []
        last_day = None
        day_meals = []
        for widget in bound_field.subwidgets:
            data = widget.data.copy()
            if data['value'] == conference_dinner_meal():
                data['conference_dinner'] = True

            meal, date = data['value'].split('_')
            date = parse_date(date)
            if date != last_day:
                day_meals = []
                by_day.append((date, day_meals))
                last_day = date

            day_meals.append(data)

        context['DEBCONF_BREAKFAST'] = settings.DEBCONF_BREAKFAST
        context['by_day'] = by_day
        return super().render(form, form_style, context, **kwargs)


class NightSelectionField(Field):
    template = 'register/fields/nights.html'
