from selenium.webdriver.common.keys import Keys

from promium.base import Element
from promium.logger import log


class InputField(Element):

    @property
    def value(self):
        """Returns attribute value"""
        return self.get_attribute("value")

    @property
    def placeholder(self):
        """Returns attribute placeholder"""
        return self.get_attribute("placeholder")

    def clear(self):
        """Clears the text if it's a text entry element."""
        return self.lookup().clear()

    def set_value(self, value):
        """Sets data by the given value"""
        self.driver.execute_script(
            'arguments[0].value = "%s"' % value, self.lookup()
        )

    def send_keys(self, *value):
        """Sends keys by the given value"""
        return self.lookup().send_keys(*value)

    def _clear_field_with_keyboard(self):
        self.send_keys(Keys.CONTROL + 'a')
        self.send_keys(Keys.BACKSPACE)

    def clear_and_fill(self, text):
        expected_text = str(text).lower()
        self._clear_field_with_keyboard()
        self.send_keys(text)
        if self.value.lower() == expected_text:
            return expected_text
        log.warning(
            f"Different text input value after clear with keyboard and fill. "
            f"Expected - {expected_text}, current - {self.value}"
        )

    def fill_field(self, text):
        expected_text = str(text).lower()
        if self.value:
            self.clear()
        self.send_keys(text)
        if self.value.lower() == expected_text:
            return expected_text
        log.warning(
            f"Different text input value after fill. "
            f"Expected - {expected_text}, current - {self.value}"
        )
