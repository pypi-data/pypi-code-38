from collections import Iterable
import csv

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import HttpResponse
from django.views.generic import ListView

from wafer.talks.models import Talk

from bursary.models import Bursary
from front_desk.models import CheckIn
from register.models import Accomm, Attendee, ChildCare, Meal
from bursary.models import Bursary


class CSVExportView(ListView):
    """Export the given columns for the model as CSV."""
    columns = None
    filename = None

    def get_data_line(self, instance):
        ret = []
        for column in self.columns:
            obj = instance
            for component in column.split('.'):
                try:
                    obj = getattr(obj, component)
                except ObjectDoesNotExist:
                    obj = '%s missing!' % component
                    break
                except AttributeError:
                    obj = getattr(self, component)(obj)
                if not obj:
                    break
                if callable(obj):
                    obj = obj()
            if (not isinstance(obj, (str, bytes))
                    and isinstance(obj, Iterable)):
                ret.extend(str(i) for i in obj)
            else:
                ret.append(str(obj))

        return ret

    def write_rows(self, writer, objects):
        for instance in objects:
            writer.writerow(self.get_data_line(instance))

    def render_to_response(self, context, **response_kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = (
            'attachment; filename="%s"' % self.filename
        )

        writer = csv.writer(response)
        writer.writerow(self.columns)
        self.write_rows(writer, context['object_list'])

        return response


class AttendeeAdminMixin(PermissionRequiredMixin):
    permission_required = 'register.change_attendee'


class AttendeeBadgeExport(AttendeeAdminMixin, CSVExportView):
    name = 'Attendee badges'
    model = Attendee
    filename = "attendee_badges.csv"
    ordering = ('user__username',)
    columns = [
        'user.username', 'reconfirm', 'user.email', 'user.get_full_name',
        'nametag_2', 'nametag_3', 'languages', 'food.diet',
    ]


class AttendeeAccommExport(AttendeeAdminMixin, CSVExportView):
    name = 'Accommodation'
    model = Accomm
    filename = "attendee_accommodation.csv"
    ordering = ('attendee__user__username',)
    columns = [
        'attendee.user.username', 'attendee.user.get_full_name',
        'attendee.user.email', 'attendee.reconfirm', 'attendee.paid',
        'attendee.user.bursary.accommodation_status', 'attendee.gender',
        'attendee.country', 'requirements',
        'family_usernames', 'get_checkin_checkouts', 'room',
    ]


class ChildCareExport(AttendeeAdminMixin, CSVExportView):
    name = 'Childcare'
    model = ChildCare
    filename = "attendee_child_care.csv"
    ordering = ('attendee__user__username',)
    columns = [
        'attendee.user.username', 'attendee.user.get_full_name',
        'attendee.user.email', 'attendee.reconfirm', 'attendee.paid',
        'attendee.user.bursary.accommodation_status',
        'attendee.arrival', 'attendee.departure',
        'needs', 'details',
    ]


class TalksExport(PermissionRequiredMixin, CSVExportView):
    name = 'Talks'
    model = Talk
    permission_required = 'talks.edit_private_notes'
    filename = "talk_evaluations.csv"
    ordering = ("talk_id",)
    columns = [
        'talk_id', 'title', 'get_authors_display_name', 'abstract',
        'talk_type.name', 'track.name', 'get_status_display', 'review_score',
        'review_count', 'notes', 'private_notes', 'all_review_comments',
    ]

    def all_review_comments(self, talk):
        return [
            "(%s) %s" % (review.reviewer.username, review.notes.raw)
            for review in talk.reviews.all()
            if review.notes.raw
        ]


class FoodExport(AttendeeAdminMixin, CSVExportView):
    name = 'Food'
    model = Meal
    filename = "meals.csv"
    ordering = ('date', 'meal',)
    columns = [
        'date', 'meal', 'total', 'total_unconfirmed',
        'regular', 'vegetarian', 'vegan', 'gluten_free',
        'other', 'other_details',
    ]

    def render_to_response(self, context, **response_kwargs):
        self._confirmed_attendees = {}
        return super().render_to_response(context, **response_kwargs)

    def attendee_confirmed(self, attendee_id):
        if attendee_id not in self._confirmed_attendees:
            if CheckIn.objects.filter(attendee_id=attendee_id).exists():
                return True

            attendee = Attendee.objects.get(id=attendee_id)
            paid = attendee.paid()

            try:
                bursary = Bursary.objects.get(user=attendee.user)
            except Bursary.DoesNotExist:
                bursary = Bursary()

            confirmed = any((
                not bursary.request_any and attendee.billable() and paid,
                not bursary.request_any and not attendee.billable() and attendee.final_dates,
                bursary.request_any and bursary.status_in(None, ['accepted']),
                attendee.reconfirm,
            ))
            self._confirmed_attendees[attendee_id] = confirmed
        return self._confirmed_attendees[attendee_id]

    def get_data_line(self, meal):
        row = {
            'date': meal.date.isoformat(),
            'meal': meal.meal,
            'total': 0,
            'total_unconfirmed': meal.food_set.count(),
            'regular': 0,
            'vegetarian': 0,
            'vegan': 0,
            'gluten_free': 0,
            'other': 0,
            'other_details': [],
        }

        for food in meal.food_set.all():
            if not self.attendee_confirmed(food.attendee_id):
                continue

            diet = food.diet
            if diet == '':
                diet = 'regular'
            elif diet == 'other':
                details = [food.attendee.user.username]
                details.append(food.special_diet)
                row['other_details'].append(': '.join(details))
            row[diet] += 1
            row['total'] += 1

        row['other_details'] = ', '.join(row['other_details'])
        return [row.get(key) for key in self.columns]


class SpecialDietExport(AttendeeAdminMixin, CSVExportView):
    name = 'Special diets'
    filename = "diets.csv"
    ordering = ('attendee__user__username',)
    columns = [
        'username', 'name', 'confirmed', 'diet', 'special_diet'
    ]

    def attendee_confirmed(self, attendee):
        try:
            if attendee.check_in:
                return True
        except CheckIn.DoesNotExist:
            pass

        if attendee.reconfirm:
            return True

        paid = attendee.paid()

        try:
            bursary = attendee.user.bursary
        except Bursary.DoesNotExist:
            bursary = Bursary()

        return any((
            not bursary.request_any and attendee.billable() and paid,
            not bursary.request_any and not attendee.billable() and attendee.final_dates,
            bursary.request_any and bursary.status_in(None, ['accepted']),
        ))

    def get_queryset(self):
        return Meal.objects.get(**self.kwargs).food_set.exclude(
                special_diet__exact='',
                diet__exact='',
            ).select_related(
                'attendee',
                'attendee__user',
                'attendee__user__bursary',
                'attendee__user__userprofile',
            ).order_by(*self.ordering)

    def get_data_line(self, food):
        row = {
            'username': food.attendee.user.username,
            'name': food.attendee.user.userprofile.display_name(),
            'confirmed': self.attendee_confirmed(food.attendee),
            'diet': food.diet,
            'special_diet': food.special_diet,
        }
        return [row.get(key) for key in self.columns]

    def write_rows(self, writer, objects):
        super().write_rows(writer, objects)
        count = {True: 0, False: 0}
        for food in Meal.objects.get(**self.kwargs).food_set.filter(
                special_diet__exact='',
                diet__exact='',
            ).select_related(
                'attendee',
                'attendee__user',
                'attendee__user__userprofile',
            ):
            count[self.attendee_confirmed(food.attendee)] += 1
        for confirmed in (True, False):
            row = {
                'username': '*',
                'name': 'Everyone Else - {} people'.format(count[confirmed]),
                'confirmed': confirmed,
                'diet': '',
                'special_diet': '',
            }
            writer.writerow([row.get(key) for key in self.columns])


class BursaryExport(AttendeeAdminMixin, CSVExportView):
    name = 'Bursaries'
    filename = "bursaries.csv"

    columns = [
        'user.username',
        'user.userprofile.display_name',
        'user.email',
        'user.attendee.country',
        'travel_from',
        'travel_status',
        'food_status',
        'accommodation_status',
    ]

    approved = ('pending', 'accepted',)

    def get_queryset(self):
        return Bursary.objects.filter(
            Q(travel_status__in=self.approved)
            | Q(food_status__in=self.approved)
            | Q(accommodation_status__in=self.approved)
        ).exclude(
            user__attendee__id=None, # exclude unregistered people
        ).prefetch_related(
            'user',
            'user__attendee',
            'user__userprofile',
        ).order_by('user__username')
