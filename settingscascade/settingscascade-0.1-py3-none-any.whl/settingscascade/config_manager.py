from collections import UserDict
from contextlib import contextmanager
from typing import List, Dict, Type, Optional, Union, KeysView, ValuesView

from sortedcontainers import SortedList


class Sections(UserDict):
    def __missing__(self, key) -> SortedList:
        section_list = SortedList(key=lambda section: -1 * len(section.selector))
        self[key] = section_list
        return section_list


class ConfigLevelMeta(type):
    def __init__(cls, name, bases, dct):
        super().__init__(name, bases, dct)
        cls.sections = Sections()
        cls.tag = dct.get("tag")
        cls.collection_tag = dct["tag"] + "s" if dct.get("tag") else None

    def build(cls, selector: Dict[str, Optional[str]], **kwargs):
        obj = cls(selector, **kwargs)
        key = selector[cls.collection_tag] if cls.collection_tag else None
        cls.sections[key].add(obj)
        return obj

    def get_value(cls, selector, key):
        sections = cls.sections.get(selector.get(cls.collection_tag))
        for section in sections:
            if hasattr(section, key) and all(
                val == (selector.get(key)) for key, val in section.selector.items()
            ):
                return getattr(section, key)
        # Check a default for this level
        sections = cls.sections.get(None)
        for section in sections:
            if hasattr(section, key) and all(
                val is None or val == (selector.get(key))
                for key, val in section.selector.items()
            ):
                return getattr(section, key)
        raise AttributeError()


class ConfigLevel(metaclass=ConfigLevelMeta):
    selector: Dict[str, str]
    tag: Optional[str]
    collection_tag: Optional[str]

    def __init__(self, selector: Dict[str, str], **kwargs):
        self.selector = selector
        for key, val in kwargs.items():
            setattr(self, key, val)


class ConfigStore:
    config_levels: Dict[Optional[str], Type[ConfigLevel]]

    def __init__(self, config_levels: List[Type[ConfigLevel]]):
        """config_levels should be from most specific to least"""
        self.config_levels = {lvl.collection_tag: lvl for lvl in config_levels}

    @property
    def tags(self) -> KeysView[Optional[str]]:
        return self.config_levels.keys()

    @property
    def levels(self) -> ValuesView[Type[ConfigLevel]]:
        return self.config_levels.values()

    def get_value(self, selector: Dict[str, str], key: str):
        for level in (
            l
            for l in self.levels
            if l.collection_tag in selector or l.collection_tag is None
        ):
            try:
                return level.get_value(selector, key)
            except AttributeError:
                continue
        raise AttributeError


class ConfigManager:
    store: ConfigStore
    levels: List[Type[ConfigLevel]]
    current_context: Dict[str, str]

    def __init__(self):
        self.store = ConfigStore(self.levels)
        data = self.get_data()
        self.load_data(data)

    def get_data(self) -> Union[list, dict]:
        raise NotImplementedError()

    @contextmanager
    def context(self, **kwargs):
        original_context = self.current_context
        self.current_context = dict(original_context, **kwargs)
        yield
        self.current_context = original_context

    def load_data(
        self,
        data: dict,
        lvl: Optional[str] = None,
        selector: Optional[Dict[str, Optional[str]]] = None,
    ):
        new_selector = {lvl: data.get("name")} if lvl else {}
        selector = dict(**(selector or {}), **new_selector)
        settings = {}
        for key, val in data.items():
            if key in self.store.tags:
                if isinstance(val, list):
                    for entry in val:
                        self.load_data(entry, key, selector)
                elif isinstance(val, dict):
                    self.load_data(val, key, selector)
                else:
                    raise RuntimeError("Cant use a tag for both a level and a setting")
            else:
                settings[key] = val
        self.store.config_levels[lvl].build(selector, **settings)

    def get_value(self, selector: Dict[str, str], key: str):
        return self.store.get_value(selector, key)

    def __getattr__(self, item):
        if item == "current_context":
            return {}
        return self.get_value(self.current_context, item)
