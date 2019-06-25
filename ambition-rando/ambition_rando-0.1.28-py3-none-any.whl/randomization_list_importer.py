import csv
import os
import sys

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.color import color_style
from tqdm import tqdm
from uuid import uuid4

from .models import RandomizationList
from .utils import get_drug_assignment, get_allocation

style = color_style()


class RandomizationListImportError(Exception):
    pass


class RandomizationListImporter:

    """Imports upon instantiation a formatted randomization CSV file
    into model RandomizationList.

    Format:
        sid,drug_assignment,site_name, orig_site, orig_allocation, orig_desc
        1,single_dose,gaborone
        2,two_doses,gaborone
        ...
    """

    def __init__(self, path=None, verbose=None, overwrite=None, add=None):
        verbose = True if verbose is None else verbose
        path = path or settings.RANDOMIZATION_LIST_PATH
        path = os.path.expanduser(path)
        if overwrite:
            RandomizationList.objects.all().delete()
        if RandomizationList.objects.all().count() > 0 and not add:
            raise RandomizationListImportError(
                "Not importing CSV. RandomizationList model is not empty!"
            )
        with open(path, "r") as csvfile:
            reader = csv.DictReader(csvfile)
            sids = [row["sid"] for row in reader]
        if len(sids) != len(list(set(sids))):
            raise RandomizationListImportError("Invalid file. Detected duplicate SIDs")
        self.sid_count = len(sids)
        self.site_names = {obj.name: obj.name for obj in Site.objects.all()}
        if not self.site_names:
            raise RandomizationListImportError(
                "No sites have been imported. See ambition-sites and ."
                'method "add_or_update_django_sites".'
            )

        objs = []
        with open(path, "r") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in tqdm(reader, total=self.sid_count):
                row = {k: v.strip() for k, v in row.items()}

                try:
                    RandomizationList.objects.get(sid=row["sid"])
                except ObjectDoesNotExist:
                    drug_assignment = get_drug_assignment(row)
                    obj = RandomizationList(
                        id=uuid4(),
                        sid=row["sid"],
                        drug_assignment=drug_assignment,
                        site_name=self.get_site_name(row),
                        allocation=get_allocation(row, drug_assignment),
                    )
                    objs.append(obj)
            RandomizationList.objects.bulk_create(objs)
            assert self.sid_count == RandomizationList.objects.all().count()

        if verbose:
            count = RandomizationList.objects.all().count()
            sys.stdout.write(style.SUCCESS(f"(*) Imported {count} SIDs from {path}.\n"))

    def get_site_name(self, row):
        """Returns the site name or raises.
        """
        try:
            site_name = self.site_names[row["site_name"]]
        except KeyError:
            raise RandomizationListImportError(
                f'Invalid site. Got {row["site_name"]}. '
                f"Expected one of {self.site_names.keys()}"
            )
        return site_name
