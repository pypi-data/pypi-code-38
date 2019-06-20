from collections import OrderedDict, defaultdict
import datetime
from itertools import repeat
import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import transaction
from django.urls import reverse
from django.views.generic.base import TemplateView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import FormView

from invoices.prices import MEAL_PRICES, invoice_user
from invoices.models import Invoice
from register.dates import (
    ARRIVE_ON_OR_AFTER, LEAVE_ON_OR_BEFORE, T_SHIRT_SWAP_ON_OR_AFTER,
    parse_date, meals as dc_meals)
from register.models import Accomm, Attendee, Food, Meal

from front_desk.forms import (
    CashInvoicePaymentForm, CheckInForm, CheckOutForm, FoodForm,
    RegisterOnSiteForm, SearchForm, ShoesForm, TShirtForm)
from front_desk.models import CheckIn

from exports.urls import exports

log = logging.getLogger(__name__)
shirt_sizes = dict(settings.DEBCONF_T_SHIRT_SIZES)


class CheckInPermissionMixin(PermissionRequiredMixin):
    permission_required = 'front_desk.change_checkin'


class CashBoxPermissionMixin(PermissionRequiredMixin):
    permission_required = 'invoices.change_invoice'


class Dashboard(CheckInPermissionMixin, TemplateView):
    template_name = 'front_desk/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = SearchForm(data=self.request.GET)

        q = None
        if form.is_valid():
            q = form.cleaned_data['q']

        results = self.search_attendees(q)
        # Strip duplicates while maintaining order
        results = list(OrderedDict(zip(results, repeat(None))))

        context.update({
            'view': self,
            'form': form,
            'results': results[:20],
            'num_results': len(results),
            'exports': exports,
        })
        return context

    def search_attendees(self, query):
        if not query:
            return

        yield from Attendee.objects.filter(user__username=query)

        if '@' in query:
            yield from Attendee.objects.filter(user__email=query)

        if ' ' in query:
            first, last = query.split(' ', 1)
            yield from Attendee.objects.filter(
                user__first_name__iexact=first,
                user__last_name__iexact=last,
            )
        yield from Attendee.objects.filter(user__username__icontains=query)
        yield from Attendee.objects.filter(user__email__icontains=query)
        yield from Attendee.objects.filter(user__first_name__icontains=query)
        yield from Attendee.objects.filter(user__last_name__icontains=query)


class CheckInView(CheckInPermissionMixin, SingleObjectMixin, FormView):
    template_name = 'front_desk/check_in.html'
    form_class = CheckInForm

    model = Attendee
    slug_field = 'user__username'
    slug_url_kwarg = 'username'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        attendee = self.object
        initial_tshirt = {
            'size': attendee.t_shirt_size,
        }
        initial_shoes = {
            'size': attendee.shoe_size,
        }

        t_shirt = 'No T-Shirt'
        if attendee.t_shirt_size:
            t_shirt = shirt_sizes[attendee.t_shirt_size]

        try:
            accomm = attendee.accomm
        except Accomm.DoesNotExist:
            accomm = None

        dates = sorted(set(date for meal, date in dc_meals(orga=True)))
        meal_labels = ['Breakfast', 'Lunch', 'Dinner']

        try:
            food = attendee.food
        except Food.DoesNotExist:
            meals = None
        else:
            meals = []
            for meal, meal_label in Meal.MEALS.items():
                cur_meal = []
                meal_dates = [entry.date
                              for entry in food.meals.filter(meal=meal)]
                for d in dates:
                    cur_meal.append((d, d in meal_dates))
                meals.append((meal_label, cur_meal))

        today = datetime.date.today()
        context.update({
            'accomm': accomm,
            'dates': dates,
            'DEBCONF_LOCAL_CURRENCY': settings.DEBCONF_LOCAL_CURRENCY,
            'DEBCONF_SHOE_SIZES': settings.DEBCONF_SHOE_SIZES,
            'invoices': Invoice.objects.filter(recipient=attendee.user),
            'meal_labels': meal_labels,
            'meals': meals,
            't_shirt': t_shirt,
            'shoes': attendee.shoe_size,
            't_shirt_form': TShirtForm(
                initial=initial_tshirt,
                username=attendee.user.username),
            'shoes_form': ShoesForm(
                initial=initial_shoes,
                username=attendee.user.username),
            't_shirt_swap_available': T_SHIRT_SWAP_ON_OR_AFTER <= today,
            'T_SHIRT_SWAP_ON_OR_AFTER': T_SHIRT_SWAP_ON_OR_AFTER,
        })
        return context

    def get_initial(self):
        try:
            check_in = self.object.check_in
        except CheckIn.DoesNotExist:
            return {}
        return {
            't_shirt': check_in.t_shirt,
            'shoes': check_in.shoes,
            'nametag': check_in.nametag,
            'notes': check_in.notes,
            'room_key': check_in.room_key,
            'key_card': check_in.key_card,
            'swag': check_in.swag,
        }

    def form_valid(self, form):
        attendee = self.object

        check_in, created = CheckIn.objects.update_or_create(
            attendee=attendee, defaults=form.cleaned_data)
        attendee.check_in = check_in

        log.info('Checked-in %s. Room Key: %s, Card: %s',
                 attendee.user.username, check_in.room_key, check_in.key_card)

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('front_desk')


class CheckOutView(CheckInPermissionMixin, SingleObjectMixin, FormView):
    template_name = 'front_desk/check_out.html'
    form_class = CheckOutForm

    model = Attendee
    slug_field = 'user__username'
    slug_url_kwarg = 'username'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def get_initial(self):
        check_in = self.object.check_in
        return {
            'returned_key': check_in.returned_key,
            'returned_card': check_in.returned_card,
            'notes': check_in.notes,
        }

    def form_valid(self, form):
        attendee = self.object

        data = form.cleaned_data
        data['checked_out'] = True

        check_in, created = CheckIn.objects.update_or_create(
            attendee=attendee, defaults=data)
        attendee.check_in = check_in

        log.info('Checked-Out %s. Returned Key: %s, Card: %s',
                 attendee.user.username, check_in.returned_key,
                 check_in.returned_card)

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('front_desk')


class ChangeFoodView(CashBoxPermissionMixin, SingleObjectMixin, FormView):
    form_class = FoodForm
    template_name = 'front_desk/change_food.html'

    model = Attendee
    slug_field = 'user__username'
    slug_url_kwarg = 'username'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.username = self.kwargs['username']
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['prices'] = MEAL_PRICES
        return context

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.username = self.kwargs['username']
        return super().post(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.object
        try:
            food = self.object.food
        except Food.DoesNotExist:
            pass
        else:
            kwargs['initial'] = {
                'meals': [meal.form_name for meal in food.meals.all()],
            }
        return kwargs

    def get_success_url(self):
        return reverse('front_desk.check_in',
                       kwargs={'username': self.username})

    def form_valid(self, form):
        data = form.cleaned_data
        user = self.object.user
        Invoice.objects.filter(
            recipient=user, status='new').update(status='canceled')
        if data['meals']:
            food, created = Food.objects.get_or_create(attendee=self.object)
            stored_meals = set(food.meals.all())
            requested_meals = set()
            for meal in data['meals']:
                meal, date = meal.split('_')
                date = parse_date(date)
                requested_meals.add(Meal.objects.get(meal=meal, date=date))

            added_meals = requested_meals - stored_meals
            removed_meals = stored_meals - requested_meals
            food.meals.remove(*removed_meals)
            food.meals.add(*added_meals)
            log.info('Modified meals for %s: Adding %s. Removing %s',
                     self.username,
                     ', '.join(sorted(str(meal) for meal in added_meals)),
                     ', '.join(sorted(str(meal) for meal in removed_meals)))
            invoice_user(user, save=True)
        else:
            Food.objects.filter(attendee=self.object).delete()
            log.info('Cancelled all meals for %s', self.username)


        return super().form_valid(form)


class ChangeShirtView(CheckInPermissionMixin, FormView):
    form_class = TShirtForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        self.username = self.kwargs['username']
        kwargs['username'] = self.username
        return kwargs

    def get_success_url(self):
        return reverse('front_desk.check_in',
                       kwargs={'username': self.username})

    def update_size(self, attendee, size):
        log.info('T-Shirt swap for %s: %s -> %s',
                 self.username, attendee.t_shirt_size, size)

        attendee.t_shirt_size = size
        attendee.save()

    @transaction.atomic
    def form_valid(self, form):
        attendee = Attendee.objects.get(user__username=self.username)
        size = form.cleaned_data['size']
        self.update_size(attendee, size)
        return super().form_valid(form)


class ChangeShoesView(ChangeShirtView):
    form_class = ShoesForm

    def update_size(self, attendee, size):
        log.info('Shoe swap for %s: %s -> %s',
                 self.username, attendee.shoe_size, size)

        attendee.shoe_size = size
        attendee.save()


class RegisterOnSite(CheckInPermissionMixin, FormView):
    form_class = RegisterOnSiteForm
    template_name = 'front_desk/register.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'ARRIVE_ON_OR_AFTER': ARRIVE_ON_OR_AFTER,
            'LEAVE_ON_OR_BEFORE': LEAVE_ON_OR_BEFORE,
        })
        return context

    @transaction.atomic
    def form_valid(self, form):
        username = form.cleaned_data['username']
        self.username = username
        email = form.cleaned_data['email']

        names = form.cleaned_data['name'].split(None, 1)
        if len(names) > 1:
            first_name, last_name = names
        else:
            first_name, last_name = names[0], ''

        user = get_user_model().objects.create_user(
            username=username, email=email, first_name=first_name,
            last_name=last_name)
        Attendee.objects.create(
            user=user, nametag_3=username, arrival=datetime.datetime.now(),
            departure=form.cleaned_data['departure'], announce_me=False,
            register_announce=False, register_discuss=False,
            final_dates=True, reconfirm=True)

        log.info('Registered on-site: %s', username)

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('front_desk.check_in',
                       kwargs={'username': self.username})


class CashInvoicePayment(CashBoxPermissionMixin, SingleObjectMixin, FormView):
    form_class = CashInvoicePaymentForm
    template_name = 'front_desk/cash_invoice_payment.html'

    model = Invoice
    slug_field = 'reference_number'
    slug_url_kwarg = 'ref'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.object
        return kwargs

    def form_valid(self, form):
        invoice = self.object
        invoice.transaction_id = 'Cash: {}'.format(
            form.cleaned_data['receipt_number'])
        invoice.status = 'paid'
        invoice.save()

        log.info('Recieved cash-payment for %s: %s',
                 invoice.recipient.username, invoice.transaction_id)

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('front_desk.check_in',
                       kwargs={'username': self.object.recipient.username})


class RoomsView(CheckInPermissionMixin, TemplateView):
    template_name = 'front_desk/rooms.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rooms = defaultdict(list)
        for accomm in Accomm.objects.select_related(
                'attendee', 'attendee__user',
                'attendee__user__userprofile',
                'attendee__check_in').all():
            room = accomm.room
            if not room:
                room = None
            rooms[room].append(accomm.attendee)

        unassigned = rooms.pop(None, [])

        if rooms:
            num_beds = max(len(occupants) for room, occupants in rooms.items())
        else:
            num_beds = 0
        bed_names = ['Bed {}'.format(i+1) for i in range(num_beds)]

        for room, occupants in rooms.items():
            occupants += [None] * (num_beds - len(occupants))

        context.update({
            'rooms': sorted(rooms.items()),
            'num_beds': num_beds,
            'bed_names': bed_names,
            'unassigned': unassigned,
        })
        return context
