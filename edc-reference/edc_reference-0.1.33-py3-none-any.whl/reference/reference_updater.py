from ..site_reference import site_reference_configs
from .reference_getter import ReferenceGetter


class ReferenceFieldNotFound(Exception):
    pass


class ReferenceUpdaterModelError(Exception):
    pass


class ReferenceUpdater:
    """Updates or creates each reference model instance; one for
    each field in `edc_reference` for this model_obj.
    """

    getter_cls = ReferenceGetter
    crf_visit_attr = "visit"

    def __init__(self, model_obj=None):

        reference_fields = site_reference_configs.get_fields(
            name=model_obj.reference_name
        )
        # loop through fields and update or create each
        # reference model instance
        for field_name in reference_fields:
            try:
                field_obj = [
                    fld
                    for fld in model_obj._meta.get_fields()
                    if fld.name == field_name
                ][0]
            except IndexError:
                raise ReferenceFieldNotFound(
                    f"Reference field not found on model. Got '{field_name}'. "
                    f"See reference {model_obj.reference_name}. "
                    f"Model fields are {[fld.name for fld in model_obj._meta.get_fields()]}"
                )
            reference = self.getter_cls(
                model_obj=model_obj, field_name=field_name, create=True
            )
            if field_obj.name == "report_datetime":
                try:
                    visit = getattr(model_obj, self.crf_visit_attr)
                    value = getattr(visit, field_name)
                except AttributeError:
                    value = getattr(model_obj, field_name)
            else:
                value = getattr(model_obj, field_name)
            try:
                value = value.pk
            except AttributeError:
                internal_type = field_obj.get_internal_type()
                related_name = None
            else:
                internal_type = "UUIDField"
                related_name = getattr(model_obj, field_name)._meta.label_lower
            reference.object.update_value(
                internal_type=internal_type, value=value, related_name=related_name
            )
            reference.object.save()
