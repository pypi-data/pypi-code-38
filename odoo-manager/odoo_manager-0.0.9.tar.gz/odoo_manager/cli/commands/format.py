import os
from .base import BaseCommand
from odoo_manager.core import shell, git

try:
    import black
except:
    print("Make sure that you have black installed before running format.")
    exit(1)


class Format(BaseCommand):
    line_length = 120
    excludes = [
        "\.container",
        "\.git",
        "\.hg",
        "\.mypy_cache",
        "\.nox",
        "\.om",
        "\.tox",
        "\.venv",
        "__manifest__.py",
        "_build",
        "_lib",
        "_lib_static",
        "dist",
        "tasks",
    ]

    def __init__(self, options, *args, **kwargs):
        """
        Initialize the supported Formatter commands.

        :return {NoneType}:
        """
        super(Format, self).__init__(options, depends_on_project=False, *args, **kwargs)
        self.supported_commands = ("html", "python", "xml")
        self.supported_extensions = ("html", "py", "xml")

    def run_html(self):
        """
        Run the HTML formatter tool, xmllint, with appropriate options.

        Example:
          # Format the given HTML file
          odoo-manager format html --source=<path/to/my/file.html

        :return {NoneType}:
        """
        source = self.options.get("--source", False)
        if not source:
            shell.out("A source file must be provided.", color="pink", is_error=True)
        if os.path.isdir(source):
            shell.out("Formatting directories is not currently supported.", color="pink", is_error=True)

        try:
            self._run_xmllint(source)
        except Exception as error:
            shell.out(
                "Standard source file failed to format. Trying again with encoding and wrapper div...", color="yellow"
            )
            try:
                # It seems that xmllint requires (A) encoding information and
                # (B) an empty "wrapper" element in order to format.
                with open(source, "r") as read_file:
                    contents = read_file.read()
                with open(source, "w") as write_file:
                    write_file.write('<?xml version="1.0" encoding="UTF-8"?>\n<div>\n' + contents + "</div>\n")

                self._run_xmllint(source)
            except Exception as error:
                shell.out("Source file failed to format even with encoding and wrapper div", color="pink", is_error=True)
                raise error
            shell.out("Source file formatting completed successfully", color="green")

    def _get_black_options(self):
        """
        Format a set of options to pass to black.

        :return {str}: Formatted set of cli options for black.
        """
        return "-l {line_length} --exclude '{excludes}'".format(
            line_length=self.line_length,
            excludes="(__manifest__.py|__openerp__.py|/({})/)".format("|".join(self.excludes)),
        )

    def run_python(self):
        """
        Run the Python formatter tool, black, with appropriate options.

        Example:
          # Format all Python files in the current directory
          odoo-manager format python

          # Format only Python files in the given path
          odoo-manager format python --source=<path/to/my/<file.py>>

        :return {NoneType}:
        """
        cmd = "black {options} {source}".format(
            options=self._get_black_options(), source=self.options.get("--source", False) or "."
        )

        if self.options.get("--verbose", False):
            shell.out(cmd)

        shell.run(cmd)

    def run_xml(self):
        """
        Run the XML formatter tool, xmllint, with appropriate options.

        Example:
          # Format the given XML file
          odoo-manager format xml --source=<path/to/my/file.html

        :return {NoneType}:
        """
        source = self.options.get("--source", False)
        if not source:
            shell.out("A source file must be provided.", color="pink", is_error=True)
        if os.path.isdir(source):
            shell.out("Formatting directories is not currently supported.", color="pink", is_error=True)

        self._run_xmllint(source)

    @staticmethod
    def _get_xmllint_command(source):
        """
        Build the `xmllint` lint command with options for the given source file.

        This formats the source file, saving the output to a temporary file,
        then finally overwrites the source file with the temporary file. The
        temporary file is required because `xmllint` does not support formatting
        files in-place.

        :param source {str}: Relative path to file being formatted.
        :return {str}:
            The `xmllint` command to be run to format the given source file.
        """
        # XMLLINT_INDENT specifies 4 spaces for indentation instead 2 (default)
        return r"XMLLINT_INDENT=\ \ \ \  xmllint --format {source} --output {source}.tmp && mv {source}.tmp {source}".format(
            source=source
        )

    def _run_xmllint(self, source):
        """
        Build and run the `xmllint` command with options for the given source
        file.

        This is to be called by a wrapper method, like `run_html` and `run_xml`
        so that each method can perform any necessary changes to the source file
        before calling the format method.

        :param source {str}: Relative path to file being formatted.
        :return {NoneType}:
        """
        cmd = self._get_xmllint_command(source)

        if self.options.get("--verbose", False):
            shell.out(cmd)

        shell.run(cmd)
