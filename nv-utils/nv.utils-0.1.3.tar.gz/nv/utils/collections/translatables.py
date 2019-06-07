from copy import copy
from collections.abc import MutableMapping


__all__ = ["TranslatableObject", "TranslatableMapMixin", "TranslatableContainer", "TranslatableString"]


class TranslatableObject:
    """
    Internationalized string stored under a Python dict.
    """

    _DEFAULT_LANGUAGE = 'en-us'
    _CURRENT_LANGUAGE = _DEFAULT_LANGUAGE
    _DEFAULT_CONTENT = None

    def __init__(self, data=None, language=None, default_language=None, fallback_language=None, container=None):

        default_language = default_language or self.get_default_language()
        language = language or default_language
        container = container or dict()

        if isinstance(container, TranslatableObject):
            self._container = container._container
        else:
            self._container = container

        self.default_language = default_language
        self.fallback_language = fallback_language or default_language
        self._container.setdefault(language, data or self._DEFAULT_CONTENT)

    def as_dict(self):
        return copy(self._container)

    def get_localized(self, language, use_fallback=True):
        local_obj = self._container.get(language, None)

        if local_obj is None:
            if use_fallback:
                local_obj = self.get_fallback()
            else:
                raise AttributeError(f"Requested locale '{language}' not found (use_fallback=False)")

        return local_obj
    
    def set_localized(self, language, value):
        self._container[language] = value

    def del_localized(self, language):
        del self._container[language]

    def get_current(self):
        return self.get_localized(self.get_current_language(), use_fallback=True)

    def get_fallback(self):
        return self._container.get(self.fallback_language, "")

    # Hooks to use in external APIs (e.g. Django)
    def get_default_language(self):
        return self._DEFAULT_LANGUAGE

    def get_current_language(self):
        return self._CURRENT_LANGUAGE

    @classmethod
    def set_current_language(cls, language):
        # This method is sets the language as a shared class variable - while this may work, this
        # is not intended to be used as such. You should always prefer overwriting get_current_language
        # and delegating the management to a broader context if possible (e.g. if you are using Django)
        TranslatableObject._CURRENT_LANGUAGE = language

    @property
    def localized(self):
        return self.get_current()

    @localized.setter
    def localized(self, value):
        self._container[self.get_current_language()] = value

    @localized.deleter
    def localized(self):
        del self._container[self.get_current_language()]

    def __str__(self):
        return self.localized.__str__()

    def __repr__(self):
        kwargs = dict()

        if self.default_language != self._DEFAULT_LANGUAGE:
            kwargs['default_language'] = self.default_language

        if self.fallback_language != self.default_language:
            kwargs['fallback_language'] = self.fallback_language

        kwargs = (", " + ', '.join(f"{k}={v!r}" for k, v in kwargs.items())) if kwargs else ""

        return f"{self.__class__.__name__}({self._container!r}{kwargs})"

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._container == other._container
        else:
            return self.localized == other

    # Proxy to access localized content directly
    def __getattr__(self, name):
        return getattr(self.localized, name)


class TranslatableMapMixin(MutableMapping):

    # Convenience access as mapping
    def __getitem__(self, key):
        return self.get_localized(key)

    def __setitem__(self, key, value):
        self.set_localized(key, value)

    def __delitem__(self, key):
        self.del_localized(key)

    def __iter__(self):
        return iter(self._container)

    def __len__(self):
        return len(self._container)


class TranslatableContainer(TranslatableMapMixin, TranslatableObject):
    pass


class TranslatableString(TranslatableMapMixin, TranslatableObject):
    _DEFAULT_CONTENT = ""

    def set_localized(self, language, value):
        super().set_localized(language, str(value))
