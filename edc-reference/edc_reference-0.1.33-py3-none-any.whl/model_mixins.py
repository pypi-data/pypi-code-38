from django.db import models

from .reference import ReferenceDeleter, ReferenceUpdater


class ReferenceModelMixinError(Exception):
    pass


class ReferenceModelMixin(models.Model):

    reference_deleter_cls = ReferenceDeleter
    reference_updater_cls = ReferenceUpdater

    def update_reference_on_save(self):
        self.model_reference_validate()
        if self.reference_updater_cls:
            self.reference_updater_cls(model_obj=self)

    def save(self, *args, **kwargs):
        self.update_reference_on_save()
        super().save(*args, **kwargs)

    @property
    def reference_name(self):
        return self._meta.label_lower

    def model_reference_validate(self):
        if "panel" in [f.name for f in self._meta.get_fields()]:
            raise ReferenceModelMixinError(
                "Detected field panel. Is this a requisition?. "
                "Use RequisitionReferenceModelMixin "
                "instead of ReferenceModelMixin"
            )

    class Meta:
        abstract = True


class RequisitionReferenceModelMixin(ReferenceModelMixin, models.Model):
    @property
    def reference_name(self):
        return f"{self._meta.label_lower}.{self.panel.name}"

    def model_reference_validate(self):
        if "panel" not in [f.name for f in self._meta.get_fields()]:
            raise ReferenceModelMixinError(
                "Did not detect field panel. Is this a CRF?. "
                "Use ReferenceModelMixin "
                "instead of RequisitionReferenceModelMixin"
            )

    class Meta:
        abstract = True
