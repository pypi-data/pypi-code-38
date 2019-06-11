import re
from pkg_resources import iter_entry_points
import sparkplug.logutils
import sparkplug.digraph as d

_log = sparkplug.logutils.LazyLogger(__name__)


# We use this for the final channel configurer (see create_configurer)
class CompositeConfigurer(object):
    def __init__(self, configurers):
        self.configurers = configurers
    
    def start(self, channel):
        for configurer in self.configurers:
            configurer.start(channel)
    
    def stop(self, channel):
        for configurer in reversed(self.configurers):
            configurer.stop(channel)


class DependencyConfigurer(object):
    def __init__(self):
        self.depends_on_names = []
        self.depended_on_names = []
    
    def depends_on(self, dependencies):
        self.depends_on_names += re.split(r"\s+", dependencies.strip())
    
    def depended_on(self, dependencies):
        self.depended_on_names += re.split(r"\s+", dependencies.strip())
    
    def start(self, channel):
        pass
    
    def stop(self, channel):
        pass


def section_dict(config, section):
    # We strip out any keys with dashes in them so that we can use them in
    # interpolation without having to pass them as kwargs to the individual
    # configuration elements.
    #
    # 'use' (which is magic for the ConsumerConfigurer entry point) is not
    # handled here - it's handled by argument scatter down at conf_entry_point
    # and ConsumerConfigurer's __init__. All other "internal" config keys
    # conform to this dash convention.
    section_dict = dict(config.items(section))
    stripped_dict = dict(
        (key, section_dict[key]) for key in section_dict if '-' not in key
    )
    return stripped_dict


def calculate_dependencies(configurers):
    """Given a dictionary of name -> DependencyConfigurer objects, returns a
    list with the leaf nodes of the implied dependencies first.
    """

    # We do this via graph theory rather than hard-coding a particular startup
    # order.
    config_graph = d.Digraph()
    for configurer in configurers.values():
        config_graph.add_node(configurer)
    for configurer_name, configurer in configurers.items():
        # Add outbound dependencies for every node.
        for name in configurer.depends_on_names:
            _log.debug("%s depends on %s", configurer_name, name)
            config_graph.add_edge(configurers[name], configurer)
        # Add inbound dependencies for every node.
        for name in configurer.depended_on_names:
            _log.debug("%s depends on %s", name, configurer_name)
            config_graph.add_edge(configurer, configurers[name])

    return config_graph.sorted()


def load_configurers(config, defaults, connector):
    configurers = {}
    for section in [section for section in config.sections() if ':' in section]:
        section_type, section_name = section.split(':', 1)
        if section_type != connector:
            section_name = section_name % defaults
            params = section_dict(config, section)
            _log.debug("Configuring %s (type %s)", section_name, section_type)
            if section_name in configurers:
                _log.error("Duplicate configuration section named %s.", section_name)
            configurers[section_name] = load_configurer(section_type, section_name, params)
    return configurers


def create_configurer(config, defaults, connector):
    # section is a list of type, name, params tuples
    configurers_by_name = load_configurers(config, defaults, connector)
    configurers = calculate_dependencies(configurers_by_name)
    _log.debug("Configurer order: %r", configurers)
    return CompositeConfigurer(configurers)


def load_configurer(type, name, params):
    return conf_entry_point('sparkplug.configurers', type, name, params)


def conf_entry_point(group, type, name, params, *args):
    for entry_point in iter_entry_points(group, type):
        connector_factory = entry_point.load()
        return connector_factory(name, *args, **params)
    raise EnvironmentError("No entry point for %r named %r found." % (group, type))


def create_connector(config, channel_configurer, connector, connection):
    _log.debug("Creating connector %s (of type %s)", connection, connector)
    
    section = "%s:%s" % (connector, connection)
    params = section_dict(config, section)

    return conf_entry_point('sparkplug.connectors', connector, connection, params,
                            channel_configurer)
