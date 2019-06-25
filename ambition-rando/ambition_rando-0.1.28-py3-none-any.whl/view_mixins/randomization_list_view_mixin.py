from django.apps import apps as django_apps
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.base import ContextMixin
from edc_identifier.utils import is_subject_identifier_or_raise

from ..randomizer import RandomizationListError


class RandomizationListViewMixin(ContextMixin):

    randomization_list_model = "ambition_rando.randomizationlist"

    @property
    def treatment_description(self):
        model_cls = django_apps.get_model(self.randomization_list_model)
        subject_identifier = is_subject_identifier_or_raise(
            self.kwargs.get("subject_identifier")
        )
        try:
            obj = model_cls.objects.get(subject_identifier=subject_identifier)
        except ObjectDoesNotExist as e:
            current_site = Site.objects.get_current()
            total = model_cls.objects.filter(site_name=current_site.name).count()
            available = model_cls.objects.filter(
                site_name=current_site.name, allocated=False
            ).count()
            raise RandomizationListError(
                f"Subject {subject_identifier}. "
                f"Found {available}/{total} available records for {current_site}. Got {e}"
            )
        return obj.treatment_description

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(treatment_description=self.treatment_description)
        return context
