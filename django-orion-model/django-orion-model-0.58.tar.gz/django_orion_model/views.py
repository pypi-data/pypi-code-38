from django.views.generic.base import View
from django.views.generic.detail import SingleObjectMixin
from django.core.exceptions import ImproperlyConfigured
from logging import getLogger


logger = getLogger(__name__)


class SubscriptionCallbackView(View):

    def get(self, request, *args, **kwargs):
        pass


class DynamicSingleObjectMixin(SingleObjectMixin):
    """Provides de capability to load a object  by a specific subclass stored in a """
    model = None
    base_model = None
    subclass_field = "subclass"
    widgets = dict()

    def get_queryset(self):
        if self.base_model:
            return self.base_model._default_manager.all()
        else:
            raise ImproperlyConfigured(
                "%(cls)s is missing a QuerySet. Define "
                "%(cls)s.model, %(cls)s.queryset, or override "
                "%(cls)s.get_queryset()." % {
                    'cls': self.__class__.__name__
                }
            )

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        try:
            return obj.subclassed()
        except AttributeError:
            logger.debug("%s is not subclassed", obj.__class__.__name__)
            return obj

    def get_form(self):
        form = super().get_form()
        for field, widget in self.widgets.items():
            form.fields[field].widget = widget
        return form
