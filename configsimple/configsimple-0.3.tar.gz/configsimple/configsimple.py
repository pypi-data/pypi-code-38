from configsimple import configargparse
import re
import sys
from loguru import logger

logger.remove()
logger.add(sys.stderr, level="INFO")

PAT_OPTION = re.compile(r'(--?)([a-zA-Z0-9][a-zA-Z0-9_.-]*)')
PAT_OPTION_TOP = re.compile(r'(-?-?)([a-zA-Z0-9][a-zA-Z0-9_.-]*)')


class ConfigSimple:
    """
    This class replaces ArgumentParser and the result of parse_args.
    It can declare and parse settings for the "top level" much like ArgumentParser does
    plus a ConfigSimple(component="somecomponent") can declare settings for a component
    with the given name which are then available as "somecomponent.settingname".
    Settings are accessed through the get(settingname) of this class.
    Component settings need to get added to a top setting instance.
    The get() method for a component retrieves only the settings for that component while
    the get() method for the top level settings object can retrieve all settings, for
    the top level (without a dot) and for all already processed component settings.
    """

    @staticmethod
    def fullname(component, option):
        """
        Returns the full option name, given a component and an option name. This is simply the two parts
        joined by a dot, or if component is the empty string, just option.
        If the option starts with one or two dashes, those dashes are moved in front.
        :param component: component name, or an empty string
        :param option: option name
        :return: full name
        """
        if component.strip() == "":
            return option
        else:
            if len(option) > 2 and option.startswith('--'):
                return '--' + component + '.' + option[2:]
            elif len(option) > 1 and option.startswith('-'):
                return '-' + component + '.' + option[1:]
            else:
                return component + "." + option

    @staticmethod
    def envname_from(prefix, component, optionname):
        newcomp = component.upper().replace(".", "_")
        newopt = optionname.upper().replace("-", "_")
        return prefix + newcomp + "_" + newopt

    def __init__(self, description=None,
                 usage=None,
                 component=None,
                 config_files=None,
                 env_var_prefix="SIMPLECONFIG_"):
        """
        Create config object, if component is not None or the empty string, it is a
        component config object which MUST be added to a top config object before it
        can be used. All settings should get accessed from the top object using
        the get() method.
        :param description: The description of the program or component
        :param usage: Override the usage information
        :param component: If None or "", a top config object, otherwise a component config
        object which must get added to a top object.
        :param config_files: the file path name of a config file to also read when parsing
        arguments, or a list of such names.
        :param env_var_prefix: the string to prepend when looking for environment variables
        for settings, default is SIMPLECONFIG_, so the name searched for setting --bar would
        be SIMPLECONFIG_BAR. For component settings a setting --comp1.foo would be
        SIMPLECONFIG_COMP1_FOO
        """
        if component is None:
            component = ""
        self.component = component
        if config_files is None:
            config_files = []
        elif not isinstance(config_files, list):
            config_files = [config_files]
        self.config_files = config_files
        self.env_var_prefix = env_var_prefix
        if component == "":
            use_env_var_prefix = None
            prog = None
        else:
            use_env_var_prefix = env_var_prefix
            prog = component
        self.argparser = configargparse.ArgParser(
            prog = prog,
            add_config_file_help=False,
            add_env_var_help=False,
            auto_env_var_prefix=use_env_var_prefix,
            ignore_unknown_config_file_keys=False,  # ???
            default_config_files=self.config_files,
            description=description,
            usage=usage,
            add_help=False,
            allow_abbrev=False,
            prefix_chars='-')
        # always add the standard options: component.help, component.config_file
        self.argparser.add(ConfigSimple.fullname(self.component, "--help"), action="store_true",
                           help="Show help for the '{}' component".format(self.component))
        self.argparser.add(ConfigSimple.fullname(self.component, "--config_file"),
                           is_config_file_arg=True,
                           help="Specify a file from which to load settings for component '{}'".
                           format(self.component))
        self.argparser.add(ConfigSimple.fullname(self.component, "--save_config_file"),
                           metavar="CONFIG_OUTPUT_PATH",
                           is_write_out_config_file_arg=True,
                           help="Specify a file to which to save specified settings.")
        logger.debug("Created argparser for {}: {}".format(self.component, self.argparser))
        logger.debug("Allow abbrev is {}".format(self.argparser.allow_abbrev))
        self.namespace = None
        self.defaults = {}   # dictionary dest->value
        self.added_configs = []
        self.known_options = set()
        self.parent = None  # this will be set if this config gets added to another config

    def get_config(self, description=None,
                 usage=None,
                 component=None,
                 config_files=None,
                 env_var_prefix="SIMPLECONFIG_"):
        if self.component != "":
            raise Exception("Cannot get a component config from a config that is not a top config but component {} config".format(self.component))
        if component is None or component == "":
            raise Exception("Can only get a component config, not a top config")
        for cfg in self.added_configs:
            if cfg.component == component:
                return cfg
        tmpconfig = ConfigSimple(description=description,
                 usage=usage,
                 component=component,
                 config_files=config_files,
                 env_var_prefix=env_var_prefix)
        self.add_config(tmpconfig)
        return tmpconfig

    def add_config(self, config):
        """
        Add the given ConfigSimple for a component to this instance. The current config must
        be a "top" component and the one added must be a component config.
        If the config is already added, the call does nothing.
        :param config: the other  config to add
        :return:
        """
        # before we add, check that the component name is not already added!
        if self.component != "":
            raise Exception("Can only add to a top config but adding to {}".format(self.component))
        if config.component == "":
            raise Exception("Can only add a component config, not a top config")
        # adding the same config twice is a NOOP
        for cfg in self.added_configs:
            if cfg.component == config.component:
                logger.debug("Component {} already added".format(config.component))
                return
        logger.debug("Adding component {}".format(config.component))
        self.added_configs.append(config)
        config.parent = self
        if config.namespace is not None:
            self.merge_namespace(config.namespace)

    def add_argument(self, *args, **kwargs):
        # intercept all the args and use componentame.optionname instead
        # NOTE: unlike with argparser, this will ignore any attempt to add the same
        # parameter twice! argparse will happily add several positional arguments with the same
        # name but we only do it the first time, argparse will complain when adding an option twice but
        # we only do it the first time.
        options_new = []
        if not args:
            raise Exception("Need at least one argument!")
        for option_string in args:
            if self.component == "":
                m = PAT_OPTION_TOP.match(option_string)
            else:
                m = PAT_OPTION.match(option_string)
            if m is None:
                raise Exception("Not a valid option string: {}".format(option_string))
            prefixchars, optionname = m.groups()
            option_new = prefixchars + ConfigSimple.fullname(self.component, optionname)
            if option_new in self.known_options:
                return
            self.known_options.add(option_new)
            options_new.append(option_new)
        # intercept the dest keyword

        kwargs.setdefault('dest', None)
        dest = kwargs.pop("dest")
        # only set the destination if this is not a positional argument
        if dest is None and options_new[0].startswith("-"):
            dest = optionname
        if dest is not None:
            dest = ConfigSimple.fullname(self.component, dest)
            kwargs["dest"] = dest
        # intercept the default value, we do not allow argparse to handle this
        kwargs.setdefault("default", None)
        default = kwargs.pop("default")
        if dest is not None:
            self.defaults[dest] = default
        if self.component != "" and self.env_var_prefix is not None:
            envname = ConfigSimple.envname_from(
                self.env_var_prefix, self.component, optionname)
            kwargs.setdefault("env_var", envname)
            logger.debug("Set env_var for {}/{} to {}".format(self.component, optionname, envname))
        # logger.debug("Defaults for {} are now {}".format(self.component, self.defaults))
        self.argparser.add_argument(*options_new, **kwargs)

    def show_help(self):
        help = self.argparser.format_help()
        print(help, sys.stderr)
        for cfg in self.added_configs:
            help = cfg.argparser.format_help()
            print(help, sys.stderr)

    def parse_args(self, args=None):
        """
        Parse the arguments for this config, if this is a component config, can only be done
        after the config has been added to a top config.
        :param args: a list of argument tokens or None to use argv[1:]
        :return: None
        """
        if self.component != "" and self.parent is None:
            raise Exception("Can only use parse_args for a component config ({}) after adding to top config".format(self.component))
        logger.debug("Trying to parse")
        # even before actually parsing, if we have a top config we check if there is a --help or -h
        # argument and process the help manually so we can include the help info for any added
        # component configs
        argstouse = args or sys.argv[1:]
        if self.component == "" and ("-h" in argstouse or "--help" in argstouse):
            self.show_help()
            sys.exit()
        self.namespace, unknown = self.argparser.parse_known_args(args)
        logger.debug("After parse_args in '{}', unknown: {}".format(self.component, unknown))
        logger.debug("Namespace for {} after parse: {}".format(self.component, vars(self.namespace)))
        # first of all, check if we have a help request:
        if self.get("help"):
            self.show_help()
            sys.exit()
        for val in unknown:
            if val.startswith("-"):
                if self.component == "":
                    m = PAT_OPTION_TOP.match(val)
                else:
                    m = PAT_OPTION.match(val)
                if m is None:
                    raise Exception("Odd unknown setting name for component {}: {}".format(self.component, val))
                prefixchars, optionname = m.groups()
                if '..' in optionname or '.-' in optionname:
                    raise Exception("Not a valid setting name: {}".format(optionname))
                # we have three situations:
                # * our component is "", then if the optionname does NOT contain a dot it is unknown
                # * the optionname starts with our component prefix, then use
                #   what is left after removing the prefix and if that does not contain a dot,
                #   it is an unknown option for us
                # * neither of the two: it must be the setting that does not concern us, fine!
                if self.component == "":
                    if "." not in optionname:
                        raise Exception("Setting {} not defined for top config".format(optionname))
                elif optionname.startswith(self.component+"."):
                    nameshortened = optionname[len(self.component)+1:]
                    if "." not in nameshortened:
                        raise Exception("Setting {} not defined for component config {}"
                                        .format(nameshortened, self.component))
        # now process any config file settings and environment settings
        # configargparse alreadt handles local files and environment vars, we handle inheritance
        # and falling back to the specified default here
        if self.parent is not None:
            # TODO: set from parent settings what is still not set
            # This would be anything that was set from a file loaded in the parent for this namespace!
            pass
        # set what is still not set from the local defaults
        for k, v in self.defaults.items():
            if getattr(self.namespace, k) is None:
                setattr(self.namespace, k, v)
        # now that we have all the settings, merge them into the global settings in
        # the parent (which will bubble up to its parent and so on)
        if self.parent is not None:
            self.parent.merge_namespace(self.namespace)

    def get(self, option, default=None, exception_if_missing=False):
        """
        Get the setting for 'option' for this component. 'option' is just the name of the
        option, without the component name which is added automatically.
        If this is called on a component config, only the component settings are accessible,
        in a top config all settings so far are accessible using the full dot notation.
        :param option: the name of the option for which to retrieve the value
        :param default: a default value if the current value of the option is None
        :param exception_if_missing: instead of returning the default value, throw an exception
        :return: the value of the option or the specified default value unless an exception is thrown
        """
        if self.namespace is None:
            raise Exception("Can only use get after parse_args has been called")
        name = ConfigSimple.fullname(self.component, option)
        d = vars(self.namespace)
        if exception_if_missing and name not in d:
            raise Exception("Setting {} not found for component '{}'".format(option, self.component))
        return d.get(name, default)

    def set(self, parm, value):
        if self.namespace is None:
            raise Exception("Can only use set after parse_args has been called")
        name = ConfigSimple.fullname(self.component, parm)
        self.namespace.setattr(name, value)
        if self.parent is not None:
            self.parent.set(name, value)

    def merge_namespace(self, ns):
        """
        Merge the given namespace into our own namespace.
        :param ns: namespace to merge into our own
        :return:
        """
        # logger.debug("Merging from NS: {}".format(ns))
        for k, v in vars(ns).items():
            # logger.debug("Merging into {}: {} <= {}".format(self.namespace, k, v))
            setattr(self.namespace, k, v)
        # logger.debug("NS IS NOW: {}".format(self.namespace))

