import arrow
import sys

from django.apps import apps as django_apps
from django.conf import settings
from .models import Reference
from .reference import ReferenceUpdater
from .site_reference import site_reference_configs


class PopulaterAttributeError(Exception):
    pass


class DryRunDummy:
    def __init__(self, **kwargs):
        pass


class Populater:

    reference_updater_cls = ReferenceUpdater

    def __init__(
        self,
        names=None,
        exclude_names=None,
        skip_existing=None,
        dry_run=None,
        delete_existing=None,
    ):
        self.skip_existing = skip_existing
        self.delete_existing = delete_existing
        if not names:
            names = list(site_reference_configs.registry)
        if not exclude_names:
            exclude_names = []
        exclude_names = [n.strip() for n in exclude_names]
        self.names = [n.strip() for n in names if n not in exclude_names]
        self.dry_run = dry_run

    def summarize(self):
        for name in self.names:
            reference_model = site_reference_configs.get_reference_model(name=name)
            reference_model_cls = django_apps.get_model(reference_model)
            count = reference_model_cls.objects.filter(model=name).count()
            sys.stdout.write(f" * {name}: {count} records\n")

    def populate(self):
        if self.dry_run:
            self.reference_updater_cls = DryRunDummy
        t_start = arrow.utcnow().to(settings.TIME_ZONE).strftime("%H:%M")
        sys.stdout.write(f"Populating reference model. Started: {t_start}\n")
        sys.stdout.write(
            f" - found {len(site_reference_configs.registry)} reference names in registry.\n"
        )
        sys.stdout.write(
            f" - running for {len(self.names)} selected reference names.\n"
        )
        if self.skip_existing:
            sys.stdout.write(f" - skipping reference names with existing references\n")
        if self.dry_run:
            sys.stdout.write(
                f" - This is a dry run. No data will be created/modified.\n"
            )

        names = [name for name in self.names if not self.skip(name=name)]

        for name in names:
            site_reference_configs.get_config(name=name)

        sys.stdout.write(f" * models are {names}    \n")

        if self.delete_existing:
            sys.stdout.write(f" * deleting existing records ... \r")
            if not self.dry_run:
                for name in names:
                    Reference.objects.filter(model=name).delete()
            sys.stdout.write(f" * deleting existing records ... done.\n")

        for name in names:
            index = 0
            sys.stdout.write(f" * {name}           \r")
            model_cls = django_apps.get_model(".".join(name.split(".")[:2]))
            qs = model_cls.objects.all()
            total = qs.count()
            sub_start_time = arrow.utcnow().to(settings.TIME_ZONE).datetime
            for index, model_obj in enumerate(qs):
                index += 1
                sub_end_time = arrow.utcnow().to(settings.TIME_ZONE).datetime
                tdelta = sub_end_time - sub_start_time
                sys.stdout.write(f" * {name} {index} / {total} ... {str(tdelta)}    \r")
                self.reference_updater_cls(model_obj=model_obj)
            sub_end_time = arrow.utcnow().to(settings.TIME_ZONE).datetime
            tdelta = sub_end_time - sub_start_time
            sys.stdout.write(
                f" * {name} {index} / {total} . OK  in {str(tdelta)}      \n"
            )
        t_end = arrow.utcnow().to(settings.TIME_ZONE).strftime("%H:%M")
        sys.stdout.write(f"Done. Ended: {t_end}\n")

    def skip(self, name=None):
        if self.skip_existing:
            reference_model = site_reference_configs.get_reference_model(name=name)
            reference_model_cls = django_apps.get_model(reference_model)
            return reference_model_cls.objects.filter(model=name).exists()
        return False
