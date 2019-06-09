from copy import copy
from django.apps import apps as django_apps

from .fieldset import Fieldset
from .refset import Refset


class LongitudinalRefsetError(Exception):
    pass


class InvalidOrdering(Exception):
    pass


class NoRefsetObjectsExist(Exception):
    pass


class LongitudinalRefset:
    """A collection of a subject's `Refset` objects for a given visit model.
    """

    fieldset_cls = Fieldset
    refset_cls = Refset

    def __init__(
        self,
        name=None,
        subject_identifier=None,
        visit_model=None,
        reference_model_cls=None,
        **options,
    ):
        self.name = name
        self.model = ".".join(name.split(".")[:2])
        self.ordering = None
        self.subject_identifier = subject_identifier
        try:
            reference_model_cls = django_apps.get_model(reference_model_cls)
        except AttributeError:
            pass
        opts = dict(
            identifier=self.subject_identifier,
            model=visit_model,
            field_name="report_datetime",
            **options,
        )
        try:
            self.visit_references = reference_model_cls.objects.filter(**opts)
        except ValueError as e:
            raise LongitudinalRefsetError(f"{e}. name={self.name}. Got {opts}.")
        self._refsets = []
        for visit_reference in self.visit_references:
            self._refsets.append(
                self.refset_cls(
                    name=self.name,
                    subject_identifier=subject_identifier,
                    report_datetime=visit_reference.report_datetime,
                    timepoint=visit_reference.timepoint,
                    reference_model_cls=reference_model_cls,
                )
            )
        self.ordering_attrs = copy(self.refset_cls.ordering_attrs)
        for refset in self._refsets:
            self.ordering_attrs.extend(list(refset._fields))
        self.ordering_attrs = list(set(self.ordering_attrs))
        self.order_by("report_datetime")

    def __repr__(self):
        return f"{self.__class__.__name__}({self._refsets})"

    def __iter__(self):
        return iter(self._refsets)

    def __getitem__(self, i):
        return self._refsets[i]

    def order_by(self, field=None):
        """Re-order the collection ref objects by a single field.
        """
        if field and field.replace("-", "") not in self.ordering_attrs:
            raise InvalidOrdering(
                f"Invalid ordering field. field={field}. Expected one of "
                f"{self.ordering_attrs}"
            )
        field = field or "report_datetime"
        self.ordering = field
        reverse = False
        if field.startswith("-"):
            field = field[1:]
            reverse = True
        try:
            self._refsets.sort(key=lambda x: getattr(x, field), reverse=reverse)
        except TypeError:
            null_refsets = [x for x in self._refsets if getattr(x, field) is None]
            notnull_refsets = [
                x for x in self._refsets if getattr(x, field) is not None
            ]
            notnull_refsets.sort(key=lambda x: getattr(x, field), reverse=reverse)
            self._refsets = notnull_refsets + null_refsets
        return self

    def fieldset(self, field_name=None):
        """Returns a FieldSet for this field name.
        """
        if not self._refsets:
            raise NoRefsetObjectsExist(
                f"No Ref objects exist for this subject. "
                f"Got subject_identifier={self.subject_identifier}"
            )
        return self.fieldset_cls(field=field_name, refsets=self._refsets)
