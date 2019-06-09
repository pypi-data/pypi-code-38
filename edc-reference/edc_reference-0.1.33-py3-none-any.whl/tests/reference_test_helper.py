from datetime import date, datetime
from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist

from ..site_reference import site_reference_configs


class ReferenceTestHelperError(Exception):
    pass


class ReferenceTestHelper:

    visit_model = None

    field_types = {
        "CharField": (str),
        "DateTimeField": (datetime),
        "DateField": (date),
        "IntegerField": (int),
    }

    def __init__(self, visit_model=None, subject_identifier=None):
        if visit_model:
            self.visit_model = visit_model
        self.subject_identifier = subject_identifier
        self.app_label = visit_model.split(".")[0]
        self.reference_model_cls = django_apps.get_model(
            site_reference_configs.get_reference_model(name=visit_model)
        )

    def get(self, **kwargs):
        return self.reference_model_cls.objects.get(**kwargs)

    def filter(self, **kwargs):
        return self.reference_model_cls.objects.filter(**kwargs)

    def create_for_model(
        self, reference_name=None, report_datetime=None, visit_code=None, **options
    ):
        for field_name in site_reference_configs.get_fields(name=reference_name):
            reference = self.reference_model_cls.objects.create(
                model=reference_name,
                identifier=self.subject_identifier,
                report_datetime=report_datetime,
                timepoint=visit_code,
                field_name=field_name,
            )
            if field_name != "report_datetime":
                try:
                    value, internal_type = options.get(field_name)
                    if internal_type not in self.field_types:
                        raise TypeError(f"Invalid internal type. Got '{internal_type}'")
                except (TypeError, ValueError) as e:
                    value = options.get(field_name)
                    internal_type = None
                    if value:
                        for field_type, datatypes in self.field_types.items():
                            if isinstance(value, datatypes):
                                internal_type = field_type
                                break
                        if not internal_type:
                            raise TypeError(
                                f"{e}. Got field_name={field_name}, value={value}"
                            )
                if value:
                    reference.update_value(value=value, internal_type=internal_type)
        return self.reference_model_cls.objects.filter(
            model=reference_name,
            identifier=self.subject_identifier,
            report_datetime=report_datetime,
        )

    def update_for_model(
        self, reference_name=None, report_datetime=None, visit_code=None, valueset=None
    ):
        for field_name, internal_type, value in valueset:
            try:
                reference = self.reference_model_cls.objects.get(
                    model=reference_name,
                    identifier=self.subject_identifier,
                    report_datetime=report_datetime,
                    timepoint=visit_code,
                    field_name=field_name,
                )
            except ObjectDoesNotExist:
                reference = self.reference_model_cls.objects.create(
                    model=reference_name,
                    identifier=self.subject_identifier,
                    report_datetime=report_datetime,
                    timepoint=visit_code,
                    field_name=field_name,
                )
            reference.update_value(value=value, internal_type=internal_type)

    def create_visit(self, report_datetime=None, timepoint=None):
        reference = self.reference_model_cls.objects.create(
            identifier=self.subject_identifier,
            model=self.visit_model,
            report_datetime=report_datetime,
            timepoint=timepoint,
            field_name="report_datetime",
        )
        return reference
