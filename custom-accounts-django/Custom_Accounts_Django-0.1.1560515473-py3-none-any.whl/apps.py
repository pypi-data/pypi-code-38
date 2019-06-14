from django.apps import AppConfig

from . import i

class CustomAccountsDjangoConfig(AppConfig):
    name = ".".join(__name__.split(".")[:i])
    label = "accounts"
    verbose_name = " ".join(x.capitalize() or "_" for x in label.split("_"))
    module_path = ".".join(__name__.split(".")[:-1])

    to_context = True
    baseurl = label
    in_nav_bar = True
