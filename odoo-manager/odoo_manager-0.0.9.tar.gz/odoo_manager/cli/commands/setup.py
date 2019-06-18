import os
from .base import BaseCommand
from odoo_manager.core import shell, git
from odoo_manager.core.configs import get_project_manifest
from odoo_manager.core.misc import cleanup

YES_OPTIONS = ("y", "ye", "yes", "ya")


class Setup(BaseCommand):
    def __init__(self, options, *args, **kwargs):
        """
        Construct a Setup command object for `odoo-manager setup`.

        :return {NoneType}:
        """
        super(Setup, self).__init__(options, *args, **kwargs)
        self.supported_commands = ("dependencies", "mapping", "version")

    def run(self):
        """
        Runs when the `odoo-manager setup` command is run.

        :return {NoneType}:
        """
        subcommand = super(Setup, self).run()

        if not subcommand:
            print("setting up")

    def run_dependencies(self):
        """
        Runs when the `odoo-manager setup dependencies` command is run.

        :return {NoneType}:
        """
        options = {
            "--no-update": self.options.get("--no-update", False),
            "--only": self.options.get("--only", False),
            "--yes": self.options.get("--yes", False),
        }

        paths = self.get_paths()
        configuration = get_project_manifest()
        cleanup()

        if "depends" in configuration:
            effected_modules = []
            problem_modules = []
            dependencies = options["--only"].split(",") if options["--only"] else configuration["depends"]
            for dependency_name in dependencies:
                if not options["--no-update"] or (
                    options["--no-update"] and not os.path.isdir(paths.base("_lib/{}".format(dependency_name)))
                ):
                    effected_modules.append(dependency_name)
                    git.diff_dependency(self.ctx, dependency_name, configuration["depends"][dependency_name])

            if problem_modules:
                shell.out("The following modules had some problem ...", color="lightred")
                shell.out("  " + str.join("\n  ", problem_modules), color="lightgrey")

            if effected_modules:
                shell.out("")
                shell.out("Adding the following modules to _lib...", color="lightblue")
                shell.out("\n---\n", color="lightblue")
                shell.out("  " + str.join("\n  ", effected_modules), color="lightgrey")
                shell.out("\n---\n", color="lightblue")

                if (
                    options["--yes"]
                    or str(
                        input(
                            "Review any diffs above. Should we continue to overwrite? This will overwrite the _lib modules listed above with files "
                            "from the dependency source (y/n) :"
                        )
                    ).lower()
                    in YES_OPTIONS
                ):
                    for dependency_name in effected_modules:
                        git.update_dependency(self.ctx, dependency_name, configuration["depends"][dependency_name])
                shell.out("\nAll done.")
            else:
                shell.out("\nEverything up to date.")

        cleanup()
