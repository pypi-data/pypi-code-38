from django.conf import settings
from django.contrib.auth.models import Permission
from django.db.models import Q


class PiiUpdater:

    default_pii_models = [
        settings.SUBJECT_CONSENT_MODEL,
        "edc_locator.subjectlocator",
        "edc_registration.registeredsubject",
    ]

    def __init__(self, extra_pii_models=None, **kwargs):
        self._pii_models = None
        self._pii_historical_models = None
        self.extra_pii_models = extra_pii_models or []

    @property
    def pii_models(self):
        if not self._pii_models:
            self._pii_models = [model for model in self.default_pii_models]
            self._pii_models.extend(self.extra_pii_models)
            self._pii_models.extend(list(self.pii_historical_models))
            self._pii_models = list(set(self._pii_models))
            self._pii_models.sort()
        return self._pii_models

    @property
    def pii_historical_models(self):
        if not self._pii_historical_models:
            self._pii_historical_models = []
            for model in self.pii_models:
                if "historical" not in model:
                    model = ".historical".join(model.split("."))
                self._pii_historical_models.append(model)
        return self._pii_historical_models

    def add_pii_permissions(self, group, view_only=None):
        """Adds PII model permissions.
        """
        pii_model_names = [m.split(".")[1] for m in self.pii_models]
        if view_only:
            permissions = Permission.objects.filter(
                (Q(codename__startswith="view") | Q(codename__startswith="display")),
                content_type__model__in=pii_model_names,
            )
        else:
            permissions = Permission.objects.filter(
                content_type__model__in=pii_model_names
            )
        for permission in permissions:
            group.permissions.add(permission)

        for model in self.pii_models:
            permissions = Permission.objects.filter(
                codename__startswith="view",
                content_type__app_label=model.split(".")[0],
                content_type__model=f"historical{model.split('.')[1]}",
            )
            for permission in permissions:
                group.permissions.add(permission)

        for permission in Permission.objects.filter(
            content_type__app_label="edc_registration",
            codename__in=[
                "add_registeredsubject",
                "delete_registeredsubject",
                "change_registeredsubject",
            ],
        ):
            group.permissions.remove(permission)
        permission = Permission.objects.get(
            content_type__app_label="edc_registration",
            codename="view_historicalregisteredsubject",
        )
        group.permissions.add(permission)
