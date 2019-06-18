import os
import re
import getpass
from urllib.parse import quote
from .base import BaseCommand
from odoo_manager.core import shell, git


class New(BaseCommand):
    def __init__(self, options, *args, **kwargs):
        """
        Construct a New command object for `odoo-manager new`.

        :return {NoneType}:
        """
        super(New, self).__init__(options, depends_on_project=False, *args, **kwargs)
        self.supported_commands = ("project", "module")

    def run_project(self):
        """
        Handles `odoo-manager new project`.

        :return {NoneType}:
        """
        shell.out("Making a new project...")

        verbose = self.options.get("--verbose", False)
        name = self.options.get("--name", False)
        branch = "master"

        if not name:
            shell.out('Missing project name. Try "odoo-manager new project --name=my_project"')
            return

        try:
            shell.run(
                'git clone git@github.com:gobluestingray/odoo_project_scaffold.git {} --branch="{}" "{}"'.format(
                    "--quiet" if not verbose else "", branch, name
                )
            )
        except:
            username = quote(input("Username? "))
            password = quote(getpass.getpass("Password? "))

            try:
                shell.run(
                    'git clone https://{}:{}@github.com/gobluestingray/odoo_project_scaffold.git --quiet --branch="{}" "{}"'.format(
                        username, password, branch, name
                    )
                )
            except:
                shell.out("Invalid credentials.", color=shell.COLOR_RED)

        shell.run('rm -rf "./{}/.git"'.format(name))
        shell.out("Successfully created the project:")
        shell.out("  name:         {}".format(name), color="lightgrey")

    def run_module(self):
        """
        Handles `odoo-manager new module`.
        """
        verbose = self.options.get("--verbose", False)
        name = input(shell.out(" > What is the technical name of the module? ", color="lightblue", run=False))
        branch = input(
            shell.out(" > What is the version of the module (9.0, 10.0, 11.0, etc.)? ", color="lightblue", run=False)
        )

        module_display_name = input(
            shell.out(" > What is the display name of the module? ", color="lightblue", run=False)
        )
        module_category = input(shell.out(" > What is the category of the module? ", color="lightblue", run=False))
        module_tagline = input(
            shell.out(" > What is a tagline for the module (1 sentence description)? ", color="lightblue", run=False)
        )
        module_summary = input(
            shell.out(" > What is a summary/short explanation of the module? ", color="lightblue", run=False)
        )

        shell.out("\n")
        shell.out("Generating the module...")

        try:
            shell.run(
                'git clone git@github.com:gobluestingray/odoo_module_scaffold.git {} --branch="{}" "{}"'.format(
                    "--quiet" if not verbose else "", branch, name
                )
            )
        except:
            username = quote(input("Username? "))
            password = quote(getpass.getpass("Password? "))

            try:
                shell.run(
                    'git clone https://{}:{}@github.com/gobluestingray/odoo_module_scaffold.git --quiet --branch="{}" "{}"'.format(
                        username, password, branch, name
                    )
                )
            except:
                shell.out("Invalid credentials.", color=shell.COLOR_RED)

        shell.run('rm -rf "./{}/.git"'.format(name))

        # Wire the defaults to the module. There are a few things that every
        # module needs:
        #
        # 1. New readme.md file
        # 2. Updated __manifest__.py
        # 3. Updated static/description/index.html
        # 4. Updated doc/index.rst
        with open("./{}/readme.md".format(name), "w") as readme_file:
            readme_file.write("# {} ({})".format(module_display_name, name))
        with open("./{}/static/description/index.html".format(name), "w") as index_html_file:
            index_html_file.write(
                """
<section class="oe_container">
    <div class="oe_row oe_spaced">
        <div class="oe_span12">
            <h2 class="oe_slogan">{}</h2>
            <h3 class="oe_slogan">{}</h3>
        </div>
    </div>
</section>\n""".format(
                    module_display_name, module_tagline
                )
            )
        with open("./{}/doc/index.rst".format(name), "w") as index_rst_file:
            content = "{} documentation.".format(name)
            index_rst_file.write("{}\n{}".format(content, "=" * len(content)))

        manifest_content = False
        manifest_files = ("__manifest__.py", "__openerp__.py")
        for potential_manifest_file in manifest_files:
            if os.path.isfile("./{}/{}".format(name, potential_manifest_file)):
                with open("./{}/{}".format(name, potential_manifest_file), "r") as manifest_file:
                    manifest_content = manifest_file.read()
                    manifest_content = re.sub(
                        r'[\'"]+name[\'"]+:\s+[\'"]+(.*)[\'"]+,',
                        "'name': '{}',".format(module_display_name),
                        manifest_content,
                    )
                    manifest_content = re.sub(
                        r'[\'"]+category[\'"]+:\s+[\'"]+(.*)[\'"]+,',
                        "'category': '{}',".format(module_category),
                        manifest_content,
                    )
                    manifest_content = re.sub(
                        r'[\'"]+version[\'"]+:\s+[\'"]+(.*)[\'"]+,',
                        "'version': '{}',".format(branch + ".0"),
                        manifest_content,
                    )
                    manifest_content = re.sub(
                        r'[\'"]+summary[\'"]+:\s+[\'"]+(.*)[\'"]+,',
                        "'summary': '{}',".format(module_tagline),
                        manifest_content,
                    )
                    manifest_content = re.sub(
                        r'[\'"]+description[\'"]+:\s+[\'"]+(.*)[\'"]+,',
                        "'description': '{}',".format(module_summary),
                        manifest_content,
                    )
                if manifest_content:
                    with open("./{}/{}".format(name, potential_manifest_file), "w") as manifest_file:
                        manifest_file.write(manifest_content)

        shell.out("Successfully created the module:")
        shell.out("  name:         {}".format(name), color="lightgrey")
        shell.out("  branch:       {}".format(branch), color="lightgrey")
        shell.out("  display name: {}".format(module_display_name), color="lightgrey")
        shell.out("  category:     {}".format(module_category), color="lightgrey")
        shell.out("  tagline:      {}".format(module_tagline), color="lightgrey")
        shell.out("  summary:      {}".format(module_summary), color="lightgrey")
