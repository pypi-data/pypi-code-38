from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.forms import Form

from bursary.models import Bursary
from register.models import Attendee, Food
from register.views.core import RegisterStep


class ReviewView(RegisterStep):
    title = 'Review'
    form_class = Form
    template_name = 'register/page/review.html'

    def get_context_data(self, **kwargs):
        user = self.request.user

        try:
            attendee = user.attendee
        except Attendee.DoesNotExist:
            attendee = None

        try:
            bursary = user.bursary
        except Bursary.DoesNotExist:
            bursary = None

        try:
            food = user.attendee.food
        except ObjectDoesNotExist:
            food = None

        try:
            accomm = user.attendee.accomm
        except ObjectDoesNotExist:
            accomm = None

        try:
            child_care = user.attendee.child_care
        except ObjectDoesNotExist:
            child_care = None

        context = super().get_context_data(**kwargs)

        context.update({
            'DEBCONF_SHOE_SIZES': settings.DEBCONF_SHOE_SIZES,
            'RECONFIRMATION': settings.RECONFIRMATION,
            'accomm': accomm,
            'attendee': attendee,
            'bursary': bursary,
            'child_care': child_care,
            'food': food,
            'profile': user.userprofile,
            'user': user,
        })

        if attendee:
            context.update({
                'fee': Attendee.FEES[attendee.fee],
                'gender': Attendee.GENDERS[attendee.gender],
                't_shirt_size':
                    dict(settings.DEBCONF_T_SHIRT_SIZES)[attendee.t_shirt_size],
            })
        if bursary:
            context['bursary_need'] = Bursary.BURSARY_NEEDS.get(bursary.need)
        if food:
            context['diet'] = Food.DIETS[food.diet]

        return context
