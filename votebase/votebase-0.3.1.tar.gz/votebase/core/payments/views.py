from abc import ABCMeta
import datetime
from django.conf import settings
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.utils.timezone import now
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from votebase.core.accounts.models import Profile
from votebase.core.payments.forms import InformationForm
from votebase.core.payments.models import Order
from votebase.core.utils.trustpay import generate_signature


class PricingView(TemplateView):
    template_name = 'payments/packages.html'

    def dispatch(self, request, *args, **kwargs):
    #        key abcd1234
    #        AID 9876543210
    #        AMT 123.45
    #        CUR EUR
    #        REF 1234567890
    #        SIG DF174E635DABBFF7897A82822521DD739AE8CC2F83D65F6448DD2FF991481EA3

        print generate_signature('abcd1234', {
            'AID': 9876543210,
            'AMT': 123.45,
            'CUR': 'EUR',
            'REF': 1234567890,
            }, toTrustPay = True)

        return super(PricingView, self).dispatch(request, *args, **kwargs)


class BuyView(FormView):
    template_name = 'payments/buy.html'
    package = None
    form_class = InformationForm
    success_url = 'payments_success'

    def get_success_url(self):
        return reverse(self.success_url)

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        self.user = request.user

        if not self.user.is_authenticated():
            return self.redirect_to_registration()

        self.initial = {
            'first_name': self.user.get_profile().first_name,
            'last_name': self.user.get_profile().last_name,
        }

        return super(BuyView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
#        create order
        order = Order(
            user=self.user,
            package=self.package,
            total=self.get_fee(),
            package_valid_to = self.get_valid_to()
        )
        order.save()

        self.object = form.save(commit=False)
        self.object.order = order
        self.object.save()

        return super(BuyView, self).form_valid(form)

    def redirect_to_registration(self):
        return_url = reverse('accounts_register')
        return_url += '?next=' + self.request.path
        return redirect(return_url)

    def get_valid_to(self):
        profile = self.user.get_profile()

        if profile.is_valid() and profile.package == self.package:
            # extend
            from_date = profile.package_valid_to
        else:
            # change of package => reset valid_to date
            from_date = now()

        return from_date + datetime.timedelta(
            days=settings.VOTEBASE_SUBSCRIPTION_PERIOD_IN_DAYS)

    def get_fee(self):
        return settings.VOTEBASE_PACKAGES_SETTINGS[self.package]['monthly_fee']

    def get_context_data(self, **kwargs):
        data = super(BuyView,self).get_context_data(**kwargs)
        data['package'] = dict(Profile.PACKAGES).get(self.package)
        data['package_valid_to'] = self.get_valid_to()
        data['package_fee'] = self.get_fee()
        return data


class BuyStandardView(BuyView):
    package = Profile.PACKAGE_STANDARD


class BuyPremiumView(BuyView):
    package = Profile.PACKAGE_PREMIUM


class CheckoutSuccess(TemplateView):
    template_name = 'payments/success.html'


class CheckoutCancel(TemplateView):
    template_name = 'payments/cancel.html'


class CheckoutError(TemplateView):
    template_name = 'payments/error.html'


class CheckoutNotify(TemplateView):
    template_name = 'payments/notify.html'
