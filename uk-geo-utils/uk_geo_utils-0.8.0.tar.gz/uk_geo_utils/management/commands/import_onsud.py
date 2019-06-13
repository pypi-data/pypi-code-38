import os
import glob
from django.db import connection
from django.db import transaction
from django.core.management.base import BaseCommand
from uk_geo_utils.helpers import get_onsud_model


class Command(BaseCommand):
    """
    To import ONSUD, grab the latest release:
    http://ons.maps.arcgis.com/home/search.html?q=ONS%20Address%20Directory&t=content
    and run
    python manage.py import_onsud /path/to/data
    """

    def add_arguments(self, parser):
        parser.add_argument(
            'path',
            help='Path to the directory containing the ONSUD CSVs'
        )
        parser.add_argument(
            '-t',
            '--transaction',
            help='Run the import in a transaction',
            action='store_true',
            default=False,
            dest='transaction'
        )

    def handle(self, *args, **kwargs):
        self.table_name = get_onsud_model()._meta.db_table
        self.path = kwargs['path']
        if kwargs['transaction']:
            with transaction.atomic():
                self.import_onsud()
        else:
            self.import_onsud()

    def import_onsud(self):
        self.table_name = get_onsud_model()._meta.db_table

        glob_str = os.path.join(self.path, "*.csv")
        files = glob.glob(glob_str)
        if not files:
            raise FileNotFoundError('No CSV files found in %s' % (self.path))

        cursor = connection.cursor()
        self.stdout.write("clearing existing data..")
        cursor.execute("TRUNCATE TABLE %s;" % (self.table_name))

        self.stdout.write("importing from files..")
        for f in files:
            self.stdout.write(f)
            with open(f, 'r') as fp:
                cursor.copy_expert("""
                    COPY %s (
                    uprn, cty, ced, lad, ward, parish, hlthau, ctry,
                    rgn, pcon, eer, ttwa, nuts, park, oa11, lsoa11, msoa11,
                    wz11, ccg, bua11, buasd11, ruc11, oac11, lep1, lep2, pfa, imd)
                    FROM STDIN (FORMAT CSV, DELIMITER ',', QUOTE '"', HEADER);
                """ % (self.table_name), fp)
        self.stdout.write("...done")
