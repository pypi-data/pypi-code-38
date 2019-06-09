import copy
import sys

from django.apps import apps as django_apps
from django.utils.module_loading import import_module, module_has_submodule

from .reference_model_config import (
    ReferenceDuplicateField,
    ReferenceModelValidationError,
)
from .reference_model_config import ReferenceFieldValidationError
from .reference_model_config import ReferenceModelConfig
from .reference_model_config import ReferenceFieldAlreadyAdded


class AlreadyRegistered(Exception):
    pass


class ReferenceConfigNotRegistered(Exception):
    pass


class RegistryNotLoaded(Exception):
    pass


class SiteReferenceConfigImportError(Exception):
    pass


class SiteReferenceConfigError(Exception):
    pass


class ReferenceUpdater:
    def update(self, name=None, fields=None, get_config=None):
        try:
            reference = get_config(name=name)
        except SiteReferenceConfigError:
            reference = ReferenceModelConfig(name=name, fields=fields)
        else:
            for field in fields:
                try:
                    reference.add_fields([field])
                except ReferenceFieldAlreadyAdded:
                    pass
        return reference


class SiteReference:

    reference_updater = ReferenceUpdater()

    def __init__(self):
        self.registry = {}
        self.loaded = False
        self.registered_from_visit_schedules = False

    def register(self, reference=None):
        if reference.name in self.registry:
            raise AlreadyRegistered(
                f"Reference fields have already been registered. "
                f"Got {reference.name}"
            )
        self.registry.update({reference.name: reference})
        self.loaded = True

    def reregister(self, reference=None):
        if reference.name not in self.registry:
            raise ReferenceConfigNotRegistered(
                f"Reregister failed. Reference model configuration has not "
                f"been registered. Got {reference.name}"
            )
        self.registry.update({reference.name: reference})

    def unregister(self, name=None):
        if name not in self.registry:
            raise ReferenceConfigNotRegistered(
                f"Unregister failed. Reference model configuration has not "
                f"been registered. Got {name}"
            )
        self.registry = {k: v for k, v in self.registry.items() if k != name}

    def get_config(self, name=None):
        try:
            reference_config = self.registry.get(name)
        except AttributeError:
            reference_config = None
        if not reference_config:
            raise SiteReferenceConfigError(
                f"Model not registered. Got {name}. Expected one of "
                f"{list(self.registry.keys())}."
            )
        return reference_config

    def get_fields(self, name=None):
        """Returns a list of fields associated with the
        reference configuration of "model".
        """
        return self.get_config(name=name).field_names

    def get_reference_model(self, name=None):
        """Returns the reference model associated with the
        reference configuration of "model".
        """
        return self.get_config(name=name).reference_model

    def check(self):
        """Validates the reference data for all classes in the
        registry.
        """
        errors = {}
        for name in self.registry:
            reference_config = self.get_config(name)
            try:
                reference_config.check()
            except (
                ReferenceDuplicateField,
                ReferenceModelValidationError,
                ReferenceFieldValidationError,
            ) as e:
                errors.update({name: str(e)})
        return errors

    def autodiscover(self, module_name=None):
        """Autodiscovers classes in the reference_model_configs.py file of any
        INSTALLED_APP.
        """
        module_name = module_name or "reference_model_configs"
        sys.stdout.write(f" * checking for {module_name} ...\n")
        for app in django_apps.app_configs:
            try:
                mod = import_module(app)
                try:
                    before_import_registry = copy.copy(site_reference_configs.registry)
                    import_module(f"{app}.{module_name}")
                    sys.stdout.write(
                        f" * registered reference model configs from application '{app}'\n"
                    )
                except Exception as e:
                    if f"No module named '{app}.{module_name}'" not in str(e):
                        site_reference_configs.registry = before_import_registry
                        if module_has_submodule(mod, module_name):
                            raise
            except ModuleNotFoundError:
                pass

    def register_from_visit_schedule(
        self, visit_models=None, extra_requisition_fields=None
    ):
        """Registers CRFs and Requisitions for all visits
        under schedules using this visit model.

        Note: Unscheduled and PRN forms are automatically add as well.
        """
        from edc_visit_schedule.site_visit_schedules import site_visit_schedules
        from edc_lab.site_labs import site_labs

        requisition_fields = [
            "requisition_datetime",
            "panel",
            "is_drawn",
            "reason_not_drawn",
        ]
        requisition_fields.extend(extra_requisition_fields or [])
        requisition_fields = list(set(requisition_fields))

        self.registered_visit_model = True
        site_labs.autodiscover(verbose=False)
        site_visit_schedules.autodiscover(verbose=False)
        for visit_schedule in site_visit_schedules.registry.values():
            for schedule in visit_schedule.schedules.values():
                reference = self.reference_updater.update(
                    name=visit_models[schedule.appointment_model],
                    fields=["report_datetime"],
                    get_config=self.get_config,
                )
                self._register_if_new(reference)
                for visit in schedule.visits.values():
                    for crf in visit.all_crfs:
                        reference = self.reference_updater.update(
                            name=crf.model,
                            fields=["report_datetime"],
                            get_config=self.get_config,
                        )
                        self._register_if_new(reference)
                    for requisition in visit.all_requisitions:
                        if not requisition.panel.requisition_model:
                            raise SiteReferenceConfigError(
                                "Requisition's panel 'requisition_model' attribute "
                                f'not set. See "{requisition}". Has the requisition '
                                "been added to a lab profile and registered? Is the "
                                "APP in INSTALLED_APPS? Currently "
                                f"registered lab profiles are {list(site_labs._registry)}."
                            )
                        reference = self.reference_updater.update(
                            name=f"{requisition.model}.{requisition.panel.name}",
                            fields=requisition_fields,
                            get_config=self.get_config,
                        )
                        self._register_if_new(reference)

    def _register_if_new(self, reference):
        try:
            self.register(reference)
        except AlreadyRegistered:
            self.reregister(reference)

    def add_fields_to_config(self, name=None, fields=None):
        reference_config = self.get_config(name=name)
        reference_config.add_fields(fields)


site_reference_configs = SiteReference()
