"""
An registry for objects by id, uuid, type.
"""

# standard libraries
import typing

# local libraries
from . import Event

# third party libraries
# None


class Singleton(type):
    def __init__(cls, name, bases, dict):
        super(Singleton, cls).__init__(name, bases, dict)
        cls.instance = None

    def __call__(cls, *args, **kw):
        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args, **kw)
        return cls.instance


class ComponentManager(metaclass=Singleton):
    """The ComponentManager is a Singleton that implements the registry."""
    def __init__(self):
        self.__component_types = dict()
        self.__components_by_type = dict()
        self.component_registered_event = Event.Event()
        self.component_unregistered_event = Event.Event()

    @property
    def _component_types(self):
        return self.__component_types

    @property
    def _components_by_type(self):
        return self.__components_by_type

    def get_components_by_type(self, component_type:str) -> typing.Set[typing.Any]:
        return self.__components_by_type.get(component_type, list())

    def register(self, component, component_types: typing.Set[str]) -> None:
        for component_type in component_types:
            assert component not in self.__components_by_type.get(component_type, set())
        for component_type in component_types:
            component_set = self.__components_by_type.setdefault(component_type, set())
            component_set.add(component)
        self.__component_types.setdefault(component, set()).update(component_types)
        self.component_registered_event.fire(component, component_types)

    def unregister(self, component, component_types: typing.Set[str] = None) -> None:
        component_types = component_types if component_types is not None else self.__component_types[component]
        for component_type in component_types:
            assert component in self.__components_by_type.get(component_type, set())
        for component_type in component_types:
            self.__components_by_type.get(component_type).remove(component)
        self.__component_types[component].difference_update(component_types)
        if len(self.__component_types[component]) == 0:
            self.__component_types.pop(component)
        self.component_unregistered_event.fire(component, component_types)


def get_components_by_type(component_type: str) -> typing.Set[typing.Any]:
    """Returns set of components matching component_type."""
    return ComponentManager().get_components_by_type(component_type)


def get_component(component_type: str) -> typing.Optional[typing.Any]:
    """Returns a single component matching component type.

    If there are multiple components matching, sorts by priority (if available) and then arbitrary.

    Priority range is 0 (low) to 100 (high). Default priority is 50.
    """
    components = get_components_by_type(component_type)

    def attrgetter(attrname, default=None):
        def inside(obj):
            return getattr(obj, attrname, default)
        return inside

    sorted_components = sorted(components, key=attrgetter("priority", 50), reverse=True)

    if len(sorted_components) > 0:
        return tuple(components)[0]

    return None

def register_component(component, component_types: typing.Set[str]) -> None:
    """Register a component and associated it with the set of types. This will trigger a component_registered_event."""
    ComponentManager().register(component, component_types)


def unregister_component(component, component_types: typing.Set[str] = None) -> None:
    """Unregister a component. This will trigger a component_unregistered_event. The component must have been previously registered."""
    ComponentManager().unregister(component, component_types)


def listen_component_registered_event(listener_fn) -> Event.EventListener:
    """Add a listener for the component registered event."""
    return ComponentManager().component_registered_event.listen(listener_fn)


def listen_component_unregistered_event(listener_fn) -> Event.EventListener:
    """Add a listener for the component unregistered event."""
    return ComponentManager().component_unregistered_event.listen(listener_fn)
