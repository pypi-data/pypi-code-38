from django.db import models

from .signals import publisher_pre_delete
from .middleware import get_draft_status


class PublisherManager(models.Manager):

    def contribute_to_class(self, model, name):
        super(PublisherManager, self).contribute_to_class(model, name)
        models.signals.pre_delete.connect(publisher_pre_delete, model)

    def drafts(self):
        return self.filter(publisher_is_draft=True)

    def published(self):
        return self.filter(publisher_is_published=True)

    def unpublished(self):
        return self.filter(publisher_is_draft=False, publisher_is_published=False)

    def current(self):
        if get_draft_status():
            return self.drafts()
        return self.published()
