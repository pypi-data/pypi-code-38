import sys

from django.core.management.base import BaseCommand

from ...migration_linter import MigrationLinter


class Command(BaseCommand):
    help = "Lint your migrations"

    def add_arguments(self, parser):
        parser.add_argument(
            "--interactive",
            dest="interactive",
            action="store_true",
            help=(
                "if specified, allows you to force a migration, even if it is determined to be backwards incompatible"
            ),
        )

        parser.add_argument(
            "--include-apps",
            nargs='+',
            dest="include_apps",
            help=("Apps to lint. If not included it will lint all"),
        )

        parser.add_argument(
            "--force-update",
            dest="force_update",
            action="store_true",
            help=(
                "overwrite existing state and use current state as source of truth."
                "This is only useful when first starting a project."
            ),
        )

        parser.add_argument(
            "--state-path",
            dest="state_path",
            default=".migration_state",
            help=(
                "The folder to store the state of all migrations"
            ),
        )

    def handle(self, *args, interactive, force_update, include_apps, state_path, **options):
        linter = MigrationLinter(
            std_out=self.stdout, state_path=state_path,
            interactive=interactive, include_apps=include_apps, force_update=force_update
        )
        result = linter.lint_all_migrations()

        if result["valid"]:
            self.stdout.write("Linting complete.")
        else:
            self.stderr.write("Linting failed. Please check errors above")

        # Exit 1 on any new migrations that are not saved to state
        if result["new"] and not interactive and not force_update:
            self.stderr.write("Migration state not up to date. Run `./manage.py lintmigrations --interactive` and commit changes")
            sys.exit(1)
