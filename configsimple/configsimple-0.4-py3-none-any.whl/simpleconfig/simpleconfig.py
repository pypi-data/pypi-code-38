#
import configargparse
import re

PAT_OPTION = re.compile(r'(--?)([^.\s]+)')


class SimpleConfig:

    @staticmethod
    def fullname(component, option):
        """
        Returns the full option name, given a component and an option name. This is simply the two parts
        joined by a dot, or if component is the empty string, just option
        :param component: component name, or an empty string
        :param option: option name
        :return: full name
        """
        if component.strip() == "":
            return option
        else:
            return component + "." + option

    def __init__(self, description=None, usage=None, component=None, config_files=None):
        if component is None:
            raise Exception("SimpleConfig component must be specified as empty string or a name")
        self.component = component
        if config_files is None:
            config_files = []
        elif not isinstance(config_files, list):
            config_files = [config_files]
        self.argparser = configargparse.ArgumentParser(
            default_config_files=config_files,
            description=description,
            usage=usage,
            add_help=False,
            allow_abbrev=False,
            prefix_chars='-')
        # always add the standard options: component.help, component.config_file
        self.argparser.add("--"+SimpleConfig.fullname(self.component, "help"), action="store_true",
                           help="Show help for the '{}' component".format(self.component))
        self.argparser.add("--"+SimpleConfig.fullname(self.component, "config_file"),
                           is_config_file_arg = True,
                           help="Specify a file from which to load settings for component '{}'".format(self.component))
        self.namespace = None
        self.defaults = {}   # dictionary dest->value
        self.added_configs = []
        self.parent = None  # this will be set if this config gets added to another config

    def add_config(self, config):
        """
        Add the given SimpleConfig to this instance. This is usually used to add a component-wise config to the
        global config. This should happen as soon as it is created and all arguments have been added, but BEFORE
        the local config parses the arguments
        :param config: the other local config to add
        :return:
        """
        # before we add, check that the component name is not already added!
        if config.component == self.component:
            raise Exception("Cannot add config, component name {} already there added".format(config.component))
        for cfg in self.added_configs:
            if cfg.component == config.component:
                raise Exception("Cannot add config, component name {} already there added".format(config.component))
        self.added_configs.append(config)
        config.parent = self

    def add_argument(self, *args, **kwargs):
        # intercept all the args and use componentame.optionname instead
        options_new = []
        for option_string in args:
            m = PAT_OPTION.match(option_string)
            if m is None:
                raise Exception("Not a valid option string: {}".format(option_string))
            prefixchars, optionname = m.groups()
            options_new = prefixchars + SimpleConfig.fullname(self.component, optionname)
        # intercept the dest keyword
        dest = kwargs.pop("dest")
        if dest is not None:
            if "." in dest:
                raise Exception("dest must not contain a dot")
            dest = SimpleConfig.fullname(self.component, dest)
            kwargs["dest"] = dest
        # intercept the default value, we do not allow argparse to handle this
        default = kwargs.pop("default")
        self.defaults[default] = default
        self.argparser.add_argument(*options_new, **kwargs)

    def parse_args(self, args=None):
        ns, unknown = self.argparser.parse_known_args(args)
        for val in unknown:
            if val.startswith("-"):
                m = PAT_OPTION.match(val)
                if m is None:
                    raise Exception("Odd unknown option name for component {}: {}".format(self.component, val))
                prefixchars, optionname = m.groups()
                # if the optionname starts with the component name, remove the component name and
                # check if the remainder contains a dot. If not, it is meant to refer to this component so it is
                # unknown and invalid
                if self.component == "":
                    nameshortened = optionname
                elif optionname.startswith(self.component+"."):
                    nameshortened = optionname[len(self.component)+1:]
                if "." not in nameshortened:
                    raise Exception("Option {} not defined for component {}".format(nameshortened, self.component))
        # now process any config file settings and environment settings
        # configargparse alreadt handles local files and environment vars, we handle inheritance
        # and falling back to the specified default here
        if self.parent is not None:
            # TODO: set from parent settings what is still not set
            pass
        # set what is still not set from the local defaults
        for k, v in self.defaults.items():
            if getattr(ns, k) is None:
                setattr(ns, k, v)
        self.namespace = ns
        # now that we have all the settings, merge them into the global settings in
        # the parent (which will bubble up to its parent and so on)
        if self.parent is not None:
            self.parent.merge_namespace(self.namespace, component=self.component)

    def get(self, parm, default=None, exception_if_missing=False):
        name = SimpleConfig.fullname(self.component, parm)
        d = self.namespace.__dict__
        if exception_if_missing and name not in d:
            raise Exception("Setting {} not found for component '{}'".format(parm, self.component))
        return d.get(name, default)

    def set(self, parm, value):
        name = SimpleConfig.fullname(self.component, parm)
        self.namespace.setattr(name, value)
        if self.parent is not None:
            self.parent.set(name, value)

    def merge_namespace(self, ns, component=''):
        """
        Merge the given namespace into our own namespace.
        :param ns: namespace to merge into our own
        :return:
        """
        for k, v in ns.__dict__.items():
            if hasattr(self.namespace, k):
                raise Exception(
                    "Component {} namespace already has {}".format(self.component, k))
            name = SimpleConfig.fullname(component, k)
            setattr(self.namespace, name, v)

