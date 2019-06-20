import datetime

import six

from django import forms
from django.conf import settings
from django.utils import timezone, dateparse
from django.utils.encoding import force_text

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Fieldset, Layout, HTML, Submit

from wafer.schedule.models import ScheduleItem, Venue

from volunteers.models import Task, TaskTemplate
from volunteers.utils import get_start_end_for_scheduleitem

# The granularity in minutes for the task filtering
MINUTE_GRANULARITY = 5


class DateTimeSelectWidget(forms.Widget):
    fields = ('day', 'hour', 'minute')

    day_field = '%s_day'
    hour_field = '%s_hour'
    minute_field = '%s_minute'

    input_type = 'select'
    select_widget = forms.widgets.Select

    template_name = 'wafer.volunteers/fields/selectdatetimefield.html'

    def __init__(self, attrs=None):
        self.attrs = attrs or {}

        self.days = []
        day = settings.VOLUNTEERS_FIRST_DAY
        while day < settings.VOLUNTEERS_LAST_DAY:
            self.days.append(day)
            day += datetime.timedelta(days=1)

        self.hours = [i for i in range(24)]

        self.minutes = []
        for x in range(60//MINUTE_GRANULARITY):
            minute = MINUTE_GRANULARITY * x
            self.minutes.append(minute)

    def get_context(self, name, value, attrs):
        context = super(DateTimeSelectWidget, self).get_context(
            name, value, attrs
        )
        datetime_context = {}

        day_attrs = context['widget']['attrs'].copy()
        day_name = self.day_field % name
        day_attrs['id'] = 'id_%s' % day_name
        day_choices = [(day, force_text(day)) for day in self.days]
        datetime_context['day'] = self.select_widget(
            attrs, choices=day_choices
        ).get_context(
            name=day_name,
            value=context['widget']['value']['day'],
            attrs=day_attrs,
        )

        hour_attrs = context['widget']['attrs'].copy()
        hour_name = self.hour_field % name
        hour_attrs['id'] = 'id_%s' % hour_name
        hour_choices = [(hour, force_text(hour)) for hour in self.hours]
        datetime_context['hour'] = self.select_widget(
            attrs, choices=hour_choices
        ).get_context(
            name=hour_name,
            value=context['widget']['value']['hour'],
            attrs=hour_attrs,
        )

        minute_attrs = context['widget']['attrs'].copy()
        minute_name = self.minute_field % name
        minute_attrs['id'] = 'id_%s' % minute_name
        minute_choices = [
            (minute, force_text(minute)) for minute in self.minutes
        ]
        datetime_context['minute'] = self.select_widget(
            attrs, choices=minute_choices
        ).get_context(
            name=minute_name,
            value=context['widget']['value']['minute'],
            attrs=minute_attrs,
        )
        subwidgets = []
        for field in self.fields:
            subwidgets.append(datetime_context[field]['widget'])
        context['widget']['subwidgets'] = subwidgets
        return context

    def decompress(self, value):
        if value:
            value = timezone.make_aware(dateparse.parse_datetime(value))
            minute = (value.minute // MINUTE_GRANULARITY) * MINUTE_GRANULARITY
            r = [str(value.date()), value.hour, minute]
            return r
        return [None, None, None]

    def value_from_datadict(self, data, files, name):
        day = data.get(self.day_field % name)
        hour = data.get(self.hour_field % name)
        minute = data.get(self.minute_field % name)

        if day and hour and minute:
            return str(
                datetime.datetime.combine(
                    dateparse.parse_date(day),
                    datetime.time(hour=int(hour), minute=int(minute)),
                )
            )

    def format_value(self, value):
        day, hour, minute = None, None, None
        if isinstance(value, (datetime.date, datetime.datetime)):
            day = value.date()
            if isinstance(value, datetime.datetime):
                hour = value.hour
                minute = value.minute
            else:
                hour = 0
                minute = 0
        elif isinstance(value, six.string_types):
            dt = timezone.make_aware(dateparse.parse_datetime(value))
            day = dt.date()
            hour = dt.hour
            minute = dt.minute

        # Round down to next MINUTE_GRANULARITY
        if minute:
            minute = minute // MINUTE_GRANULARITY * MINUTE_GRANULARITY

        return {
            'day': day,
            'hour': hour,
            'minute': minute,
        }


class TasksFilterForm(forms.Form):
    start = forms.DateTimeField(label='Tasks starting', required=False,
                                widget=DateTimeSelectWidget())
    end = forms.DateTimeField(label='Tasks until', required=False,
                              widget=DateTimeSelectWidget())
    extra_filters = forms.MultipleChoiceField(
        label='Extra filters',
        choices=(
            ('needed', 'Volunteers needed'),
            ('preferred', 'Preferred tasks only'),
        ),
        required=False,
        widget=forms.CheckboxSelectMultiple(),
    )

    def __init__(self, *args, **kwargs):
        now = timezone.now()
        kwargs['initial'] = {
            'start': str(timezone.make_naive(now)),
            'end': str(timezone.make_naive(now + datetime.timedelta(days=1))),
            'extra_filters': 'needed',
        }

        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.disable_csrf = True

        self.helper.layout = Layout(
            'start',
            'end',
            'extra_filters',
        )
        self.helper.add_input(
            Submit('submit', 'Update filter', css_class='btn btn-success')
        )


class VideoMassCreateTaskForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        video_tasks = TaskTemplate.objects.filter(video_task=True)
        # FIXME - mark venues with video
        schedule_items = list(
            ScheduleItem.objects.filter(
                talk__video=True,
                venue__notes__icontains='has video coverage'
            ).all()
        )
        venues = Venue.objects.filter(
            notes__icontains='has video coverage').all()
        schedule_items.sort(key=lambda si: si.get_start_datetime())

        venue_divs = {venue.pk: Div(HTML('<h3>%s</h3>' % venue.name),
                                    css_class='venue-%s' % venue.pk)
                      for venue in venues}
        for schedule_item in schedule_items:
            tasks_for_item = Fieldset(legend='%s - %s - %s' % (
                schedule_item.venue.name,
                schedule_item.get_start_time(),
                schedule_item.talk.title,
            ))
            for task in video_tasks:
                fieldname = '%s:%s' % (schedule_item.pk, task.pk)
                initial = Task.objects.filter(schedule_item=schedule_item,
                                              template=task).exists()
                self.fields[fieldname] = forms.BooleanField(
                    required=False,
                    label=task.name,
                    initial=initial,
                )
                tasks_for_item.append(fieldname)
            venue_divs[schedule_item.venue.pk].append(tasks_for_item)

        self.helper = FormHelper()
        self.helper.layout = Layout(*venue_divs.values())
        self.helper.add_input(Submit('submit', 'Create Tasks'))

    def clean(self):
        cleaned_data = super().clean()
        new_data = {}
        for pks, create_task in cleaned_data.items():
            schedule_item_pk, task_template_pk = map(int, pks.split(':'))
            si = ScheduleItem.objects.get(pk=schedule_item_pk)
            template = TaskTemplate.objects.get(pk=task_template_pk)

            start, end = get_start_end_for_scheduleitem(si)

            task_data = {
                'start': start,
                'end': end,
                'venue': si.venue,
            }

            if create_task:
                task = Task.objects.get_or_create(schedule_item=si,
                                                  template=template,
                                                  defaults=task_data)
                new_data[(si, template)] = task
            else:
                Task.objects.filter(
                    schedule_item=si, template=template).delete()
                new_data[(si, template)] = None
        cleaned_data.update(new_data)
        return cleaned_data
