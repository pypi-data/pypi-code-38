from contextlib import contextmanager
from typing import Callable, List, Optional, Set

from jinja2 import Environment
from jinja2.meta import find_undeclared_variables

from settingscascade.selector import Item, Selector, SelectorStorage


class RuleSet:
    def __init__(self, selector: str, **kwargs):
        self.selector: Selector = Selector(selector)
        for key, val in kwargs.items():
            setattr(self, key, val)


class ConfigManager:
    def __init__(self, data: dict, levels: Optional[Set[str]] = None):
        """The top level data MUST be a dictionary, while subkeys can be
        dictionaries or lists of dictionaries
        """
        self.levels: Set[str] = levels or set()
        self.store: SelectorStorage = SelectorStorage()
        self._contexts: List[str] = [""]
        self.load_data(data, "")
        self.jinja_env: Environment = Environment()

    def add_filter(self, name: str, func: Callable):
        self.jinja_env.filters[name] = func

    @property
    def current_context(self):
        return " ".join(self._contexts)

    @contextmanager
    def context(self, new_context: str = ""):
        self.push_context(new_context)
        yield
        self.pop_context()

    def push_context(self, new_context: str = ""):
        self._contexts.append(new_context)

    def pop_context(self):
        if self._contexts:
            self._contexts.pop()

    def clear_context(self):
        self._contexts = [""]

    def load_data(self, data: dict, map_key: str, selector: str = ""):
        selector = selector + " " + map_key if selector else map_key
        selector = selector + "." + data.pop("_name_") if "_name_" in data else selector
        selector = selector + "#" + data.pop("_id_") if "_id_" in data else selector

        settings = {}
        for key, val in data.items():
            if key in self.levels or Item(key).score > (0, 0, 1):
                if isinstance(val, list):
                    for entry in val:
                        self.load_data(entry, key, selector)
                elif isinstance(val, dict):
                    self.load_data(val, key, selector)
                else:
                    raise RuntimeError("Cant use a tag for both a level and a setting")
            else:
                settings[key] = val
        self.store.add(RuleSet(selector, **settings))

    def get_value(self, selector: str, key: str):
        val = self.lookup_value(selector, key)
        # Only strings will get passed to the jinja templater
        if not isinstance(val, str):
            return val
        return self.render_value(selector, val)

    def __getattr__(self, item):
        return self.get_value(self.current_context, item)

    def render_value(self, selector, val):
        missing_keys = find_undeclared_variables(self.jinja_env.parse(val))
        template_context = {key: self.get_value(selector, key) for key in missing_keys}
        return self.jinja_env.from_string(val).render(**template_context)

    def lookup_value(self, selector: str, key: str):
        for rule in self.store.lookup_rules(selector):
            if hasattr(rule, key):
                return getattr(rule, key)
        raise ValueError()
