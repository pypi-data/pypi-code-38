import os
import string
import logging
import sys
import importlib.util
import subprocess
import shutil

from gdaps.pluginmanager import PluginManager
from .startplugin import get_user_data

from django.conf import settings
from gdaps.conf import gdaps_settings
from django.core.exceptions import ValidationError
from django.core.management.base import CommandError, BaseCommand
from django.core.management.templates import TemplateCommand
from django.apps import apps

logger = logging.getLogger(__name__)


class Command(TemplateCommand):

    _django_root: str = settings.ROOT_URLCONF.split(".")[0]

    help = "Extends a plugin with an js frontend. "

    def add_arguments(self, parser):
        parser.add_argument("plugin", type=str)
        parser.add_argument("engine", type=str)

        parser.add_argument("--install", nargs="?", const=True, default=False)
        parser.add_argument("--build", nargs="?", const=True, default=False)
        parser.add_argument("--remove", nargs="?", const=True, default=False)

    def handle(self, *args, **options):

        plugin_path = PluginManager.plugin_path
        target = os.path.join(*plugin_path.split("."), options["plugin"])
        plugin_path_full = "{base_dir}/{plugin}".format(
            plugin=target, base_dir=settings.BASE_DIR
        )

        # check if the plugin already exists
        if not os.path.exists(target):
            raise CommandError("'{}' does not exist".format(target))

        # check if the engine is supported
        if options["engine"] not in ["vue"]:
            raise CommandError(
                "'{}' is not supported as frontend engine.".format(options["engine"])
            )

        # TODO: ask the user for package.json settings (name, version, license, etc.)

        # preparation
        options["upper_cased_app_name"] = options["plugin"].upper()
        options["project_name"] = self._django_root
        options["plugin_path"] = plugin_path
        options["project_title"] = self._django_root.capitalize()
        options["files"] = []
        options["extensions"] = []

        # extend a plugin with vuejs
        if options["engine"] == "vue":

            if options["remove"]:
                if os.path.exists("{}/frontend".format(plugin_path_full)):
                    shutil.rmtree("{}/frontend".format(plugin_path_full))

            if options["install"]:

                if not os.path.exists("{}/frontend".format(plugin_path_full)):
                    os.mkdir("{}/frontend".format(plugin_path_full))

                # create files
                template = os.path.join(
                    apps.get_app_config("gdaps").path,
                    "management",
                    "templates",
                    "extension",
                    "frontend",
                    "vue",
                )
                options["files"] += [
                    "package.json",  # contains dependencies
                    "webpack.config.js",
                    ".babelrc",
                    ".editorconfig",
                    # simple vue application
                    "vue/App.vue",
                    "vue/main.js",
                    "vue/assets/logo.png",
                ]
                super().handle(
                    "app",
                    options["plugin"],
                    "{}/frontend".format(plugin_path_full),
                    template=template,
                    **options
                )

                # npm install vue
                subprocess.check_call(
                    "npm install --prefix {base_dir}/{plugin}/frontend".format(
                        plugin=target, base_dir=settings.BASE_DIR
                    ),
                    shell=True,
                )

        # compile it
        if options["build"]:

            # build
            subprocess.check_call(
                "npm run build --prefix {base_dir}/{plugin}/frontend".format(
                    plugin=target, base_dir=settings.BASE_DIR
                ),
                shell=True,
            )

            # ask the user to be sure to copy the static files
            subprocess.check_call(
                "./manage.py collectstatic".format(
                    plugin=target, base_dir=settings.BASE_DIR
                ),
                shell=True,
            )
