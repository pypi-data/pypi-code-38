from django.apps import apps as django_apps


class ReferenceModelValidationError(Exception):
    pass


class ReferenceFieldValidationError(Exception):
    pass


class ReferenceDuplicateField(Exception):
    pass


class ReferenceFieldAlreadyAdded(Exception):
    pass


class ReferenceModelConfig:

    reference_model = "edc_reference.reference"

    def __init__(self, name=None, fields=None):
        """
        Keywords:
            name = app_label.model_name for CRFs
            name = app_label.model_name.panel for Requisitions
        """

        if not fields:
            raise ReferenceFieldValidationError("No fields declared.")
        self.field_names = list(set(fields))
        self.field_names.sort()
        self.name = name.lower()
        self.model = ".".join(name.split(".")[:2])

        if len(fields) != len(self.field_names):
            raise ReferenceDuplicateField(
                f"Duplicate field detected. Got {fields}. See '{self.name}'"
            )

    def add_fields(self, fields=None):
        for field_name in fields:
            if field_name in self.field_names:
                raise ReferenceFieldAlreadyAdded(
                    f"Field already added. Got {field_name}. See '{self.name}'"
                )
        self.field_names.extend(fields)
        self.field_names = list(set(self.field_names))
        self.field_names.sort()

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name}, fields={self.field_names})"

    def check(self):
        """Validates the model class by doing a django.get_model lookup
        and confirming all fields exist on the model class.
        """
        try:
            model_cls = django_apps.get_model(self.model)
        except LookupError:
            raise ReferenceModelValidationError(
                f"Invalid app label or model name. Got {self.model}. See {repr(self)}."
            )
        model_field_names = [fld.name for fld in model_cls._meta.get_fields()]
        for field_name in self.field_names:
            if field_name not in model_field_names:
                raise ReferenceFieldValidationError(
                    f"Invalid reference field. Got {field_name} not found "
                    f"on model {repr(model_cls)}. See {repr(self)}."
                )
        try:
            model_cls.reference_updater_cls
            model_cls.reference_deleter_cls
        except AttributeError:
            raise ReferenceFieldValidationError(
                f"Missing reference model mixin. See model {repr(model_cls)}"
            )
