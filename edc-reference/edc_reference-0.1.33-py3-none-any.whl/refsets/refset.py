from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db.models import query
from ..site_reference import site_reference_configs, SiteReferenceConfigError


class RefsetError(Exception):
    pass


class RefsetOverlappingField(Exception):
    pass


class Refset:
    """An class that represents a queryset of a subject's references for a
    timepoint as a single object.
    """

    ordering_attrs = ["report_datetime", "timepoint"]

    def __init__(
        self,
        name=None,
        subject_identifier=None,
        report_datetime=None,
        timepoint=None,
        reference_model_cls=None,
    ):
        # checking for these values so that field values
        # that are None are so because the reference instance
        # does not exist and not because these values were none.
        self._fields = {}
        if not report_datetime:
            raise RefsetError("Expected report_datetime. Got None")
        if not timepoint:
            raise RefsetError("Expected timepoint. Got None")
        if not subject_identifier:
            raise RefsetError("Expected subject_identifier. Got None")
        self.subject_identifier = subject_identifier
        self.report_datetime = report_datetime
        self.timepoint = timepoint
        self.name = name
        self.reference_model_cls = reference_model_cls

        self.model = ".".join(name.split(".")[:2])

        try:
            self._fields = dict.fromkeys(
                site_reference_configs.get_fields(name=self.name)
            )
        except SiteReferenceConfigError as e:
            raise RefsetError(f"{e}. See {repr(self)}")
        try:
            self._fields.pop("report_datetime")
        except KeyError:
            pass

        self._update_fields()

    def _update_fields(self, **kwargs):
        """Gets and updates each reference model instance for
        each field.
        """
        try:
            references = list(
                self.reference_model_cls.objects.filter(
                    identifier=self.subject_identifier,
                    timepoint=self.timepoint,
                    model=self.name,
                )
            )
        except AttributeError as e:
            raise RefsetError(e)

        if len(references) == 0:
            self._fields.update(report_datetime=None)
            for field_name in self._fields:
                self._fields.update({field_name: None})
                setattr(self, field_name, None)
        else:
            for field_name in self._fields:
                try:
                    obj = [obj for obj in references if obj.field_name == field_name][0]
                except IndexError:
                    self._fields.update({field_name: None})
                else:
                    self._fields.update({field_name: obj.value})
            for key, value in self._fields.items():
                try:
                    existing_value = getattr(self, key)
                except AttributeError:
                    setattr(self, key, value)
                else:
                    if existing_value != value:
                        raise RefsetOverlappingField(
                            f"Attribute {key} already exists with a different value. "
                            f"Got {existing_value} == {value}. See {self.name}"
                        )
            self._fields.update(report_datetime=self.report_datetime)
            self._fields.update(visit_code=self.timepoint)

    @property
    def visit_code(self):
        return self.timepoint

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(name={self.name},"
            f"subject_identifier={self.subject_identifier},"
            f"timepoint={self.timepoint}) <{[f for f in self._fields]}>"
        )
