from django.contrib.auth.mixins import (
    LoginRequiredMixin, PermissionRequiredMixin)
from django.contrib.messages.views import SuccessMessageMixin
from django.http import Http404
from django.urls import reverse_lazy
from django.views.generic import FormView, UpdateView

from bursary.forms import (BursaryRefereeAddForm, BursaryUpdateForm,
                           BursaryMassUpdateForm)
from bursary.models import Bursary, BursaryReferee
from exports.views import CSVExportView


class BursaryAdminMixin(PermissionRequiredMixin):
    permission_required = 'bursary.add_bursaryreferee'


class BursaryRequestExport(BursaryAdminMixin, CSVExportView):
    model = Bursary
    filename = "bursaries.csv"
    ordering = ('user__username',)
    columns = [
        'user.username', 'user.email', 'user.first_name', 'user.last_name',
        'user.attendee.arrival', 'user.attendee.departure',
        'user.attendee.final_dates', 'user.attendee.reconfirm',
        'request_food', 'request_accommodation', 'request_travel',
        'reason_contribution', 'reason_plans', 'reason_diversity', 'need',
        'travel_bursary', 'travel_from',
        'accommodation_status', 'accommodation_accept_before',
        'food_status', 'food_accept_before',
        'travel_status', 'travel_accept_before',
        'reimbursed_amount',
    ]


class BursaryRefereeExport(BursaryAdminMixin, CSVExportView):
    model = BursaryReferee
    filename = "bursary_referees.csv"
    ordering = ('bursary__user__username', 'referee__username')
    columns = [
        'bursary.user.username', 'referee.username', 'final', 'contrib_score',
        'outreach_score', 'notes',
    ]


class BursaryRefereeAdd(BursaryAdminMixin, FormView):
    form_class = BursaryRefereeAddForm
    template_name = 'wafer/base_form.html'
    success_url = reverse_lazy('admin:bursary_bursaryreferee_changelist')

    def form_valid(self, form):
        new_referees = form.cleaned_data['to_add']
        referee_users = form.cleaned_data['referees']
        bursary_requests = form.cleaned_data['bursaries']
        for requestor, referees in new_referees.items():
            for referee in referees:
                BursaryReferee.objects.get_or_create(
                    bursary=bursary_requests[requestor],
                    referee=referee_users[referee],
                )
        return super(BursaryRefereeAdd, self).form_valid(form)


class BursaryMassUpdate(BursaryAdminMixin, FormView):
    form_class = BursaryMassUpdateForm
    template_name = 'wafer/base_form.html'
    success_url = reverse_lazy('admin:bursary_bursary_changelist')

    def form_valid(self, form):
        bursaries = form.cleaned_data['bursaries']
        notifies = form.cleaned_data['notifies']

        for bursary in bursaries:
            bursary.save()
            if bursary in notifies:
                bursary.notify_status(self.request)

        return super(BursaryMassUpdate, self).form_valid(form)


class BursaryUpdate(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Bursary
    form_class = BursaryUpdateForm
    template_name = 'bursary/update.html'
    success_message = 'Bursary request updated successfully'

    def get_object(self):
        try:
            bursary = Bursary.objects.get(user=self.request.user)
        except Bursary.DoesNotExist:
            raise Http404('No bursary request submitted')
        else:
            if not bursary.request_any:
                raise Http404('Bursary request was withdrawn')
            if not bursary.can_update():
                raise Http404('Bursary cannot be updated')
            return bursary

    def get_success_url(self):
        return reverse_lazy('wafer_user_profile',
                            args=(self.request.user.username,))
