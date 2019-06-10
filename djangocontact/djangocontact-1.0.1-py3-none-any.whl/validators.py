from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


# Custom validator here.
def validate_subject(value):

    if value == 'kishan':
        raise ValidationError(_("The name kishan is invalid."))
    return value