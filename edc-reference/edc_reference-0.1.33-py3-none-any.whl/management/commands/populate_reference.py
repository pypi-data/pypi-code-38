from django.core.management.base import BaseCommand
from edc_constants.constants import YES, NO

from ...populater import Populater


class Command(BaseCommand):

    help = "Populates the reference model"

    def add_arguments(self, parser):

        parser.add_argument(
            "--names",
            dest="names",
            nargs="*",
            default=None,
            help=(
                "run for a select list of reference names (label_lower or panel_name)"
            ),
        )
        parser.add_argument(
            "--exclude_names",
            dest="exclude_names",
            nargs="*",
            default=None,
            help="exclude reference names (label_lower or panel_name)",
        )

        parser.add_argument(
            "--skip-existing",
            dest="skip_existing",
            nargs="?",
            choices=[YES, NO],
            default=NO,
            const=YES,
            help=(f"skip reference name if records already exist (Default: {NO})"),
        )

        parser.add_argument(
            "--summarize",
            dest="summarize",
            nargs="?",
            choices=[YES, NO],
            const=YES,
            default=NO,
            help=(f"Summarize existing data (Default: {NO})"),
        )

        parser.add_argument(
            "--dry-run",
            dest="dry_run",
            nargs="?",
            choices=[YES, NO],
            const=YES,
            default=NO,
            help=(f"Summarize existing data (Default: {NO})"),
        )

        parser.add_argument(
            "--delete-existing",
            dest="delete_existing",
            nargs="?",
            choices=[YES, NO],
            const=YES,
            default=NO,
            help=(f"Delete existing data (Default: {NO})"),
        )

    def handle(self, *args, **options):
        names = options.get("names")
        exclude_names = options.get("exclude_names")
        skip_existing = options.get("skip_existing")
        skip_existing = None if skip_existing == NO else YES
        delete_existing = options.get("delete_existing")
        delete_existing = None if delete_existing == NO else YES
        summarize = options.get("summarize")
        summarize = None if summarize == NO else YES
        dry_run = options.get("dry_run")
        dry_run = None if dry_run == NO else YES
        populater = Populater(
            names=names,
            exclude_names=exclude_names,
            skip_existing=skip_existing,
            delete_existing=delete_existing,
            dry_run=dry_run,
        )
        if summarize:
            populater.summarize()
        else:
            populater.populate()
