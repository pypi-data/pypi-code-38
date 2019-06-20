from django.conf import settings
from django.forms import Form

from register.views.core import RegisterStep

class InstructionsView(RegisterStep):
    template_name = "register/page/instructions.html"
    title = 'Instructions'
    form_class = Form  # Square peg in a round hole

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'DEBCONF_PAID_ACCOMMODATION': settings.DEBCONF_PAID_ACCOMMODATION,
            'DEBCONF_CONFIRMATION_DEADLINE':
                settings.DEBCONF_CONFIRMATION_DEADLINE,
            'DEBCONF_BURSARY_DEADLINE':
                settings.DEBCONF_BURSARY_DEADLINE,
        })
        return context
