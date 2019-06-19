from . import Registration
from django_adminstats import qs


class ModelRegistration(Registration):

    def __init__(self, model):
        self.model = model
        self.meta = getattr(self.model, '_meta')

    def get_queryset(self):
        return self.model.objects

    @property
    def key(self):
        return '{}.{}'.format(self.meta.app_label, self.meta.model_name)

    @property
    def label(self):
        return self.meta.verbose_name_plural.title()

    def query_options(self, text: str, *, is_filter: bool = False) -> list:
        """Given a filter string, return the next options"""
        part = qs.QuerySpecPart(text, is_filter=is_filter)
        return part.options(self.model)
