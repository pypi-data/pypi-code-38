
import random

from selenium.webdriver.support.select import Select

from promium.base import Element


class DropDown(Element):

    @property
    def drop_down(self):
        return Select(self.lookup())

    @property
    def options(self):
        """Gets drop down options list"""
        return self.drop_down.options

    def select_by_visible_text(self, text):
        """Selects the option by the visible_text"""
        return self.drop_down.select_by_visible_text(text)

    def select_by_value(self, value):
        """Selects the option by the given value"""
        return self.drop_down.select_by_value(value)

    def select_random_option(self, without_first=False):
        """Selects random option with or without default empty one"""
        options = self.options[1:] if without_first else self.options
        selectable_option = random.choice(options).get_attribute('value')
        return self.select_by_value(selectable_option)
