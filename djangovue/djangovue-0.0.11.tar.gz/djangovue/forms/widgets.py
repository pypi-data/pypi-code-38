from typing import Dict, Any
from django.forms import widgets


class VueWidget:
    LAZY = "lazy"
    TRIM = "trim"
    NUMBER = "number"

    def __init__(
        self, *args, model: str = None, modifier: str = None, **kwargs
    ) -> None:
        """Sets django vue specific widget attributes."""

        super().__init__(*args, **kwargs)

        self._model = model
        self._modifier = modifier

    @property
    def vmodel_attribute(self) -> str:
        """Return the v-model attribute with the modifier if provided."""

        if self._modifier is not None:
            return f"v-model.{self._modifier}"
        else:
            return "v-model"

    @property
    def modifier(self):
        return self._modifier

    def render(self, name: str, value: Any, attrs: Dict = None, renderer: Any = None):
        """Render the widget as an HTML string."""

        if attrs is None:
            attrs = {self.vmodel_attribute: self._model or name}
        else:
            attrs.update({self.vmodel_attribute: self._model or name})

        context = self.get_context(name, value, attrs)
        return self._render(self.template_name, context, renderer)


class TextInput(VueWidget, widgets.TextInput):
    """Custom text input which applies v-model binding."""

    pass


class NumberInput(VueWidget, widgets.NumberInput):
    """Custom number input which applies v-model binding."""

    pass


class EmailInput(VueWidget, widgets.EmailInput):
    """Custom email input which applies v-model binding."""

    pass


class URLInput(VueWidget, widgets.URLInput):
    """Custom url input which applies v-model binding."""

    pass


class PasswordInput(VueWidget, widgets.PasswordInput):
    """Custom url input which applies v-model binding."""

    pass


class HiddenInput(VueWidget, widgets.HiddenInput):
    """Custom url input which applies v-model binding."""

    pass


class FileInput(VueWidget, widgets.FileInput):
    """Custom url input which applies v-model binding."""

    pass


class Textarea(VueWidget, widgets.Textarea):
    """Custom text area input which applies v-model binding."""

    pass


class DateTimeBaseInput(TextInput):
    """Custom date input which applies v-model binding."""

    pass


class DateInput(DateTimeBaseInput):
    """Custom date input which applies v-model binding."""

    pass


class DateTimeInput(DateTimeBaseInput):
    """Custom datetime input which applies v-model binding."""

    pass


class TimeInput(DateTimeBaseInput):
    """Custom datetime input which applies v-model binding."""

    pass


class CheckboxInput(VueWidget, widgets.CheckboxInput):
    """Custom checkbox input which applies v-model binding."""

    pass


class RadioSelect(VueWidget, widgets.RadioSelect):
    """Custom radio input which applies v-model binding."""

    pass


class Select(VueWidget, widgets.Select):
    """Custom select which applies v-model binding."""

    pass


class SelectMultiple(VueWidget, widgets.SelectMultiple):
    """Custom select which applies v-model binding."""

    pass


class NullBooleanSelect(VueWidget, widgets.NullBooleanSelect):
    """Custom null boolean select which applies v-model binding."""

    pass
