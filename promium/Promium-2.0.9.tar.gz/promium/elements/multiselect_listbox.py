
from selenium.webdriver.support.select import Select

from promium.base import Element


class MultiSelectListBox(Element):

    @property
    def listbox(self):
        return Select(self.lookup())

    @property
    def options(self):
        """Gets drop down options list"""
        return self.listbox.options

    def deselect_all(self):
        """Deselects all options"""
        for opt in self.options:
            if opt.is_selected():
                opt.click()

    def select_by_visible_text(self, text):
        """Selects the option by the visible_text"""
        return self.listbox.select_by_visible_text(text)
