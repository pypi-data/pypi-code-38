
from promium.base import Element


class Checkbox(Element):

    def select(self):
        """Selects checkbox from any default state"""
        if not self.is_selected():
            self.click()

    def deselect(self):
        """Deselects checkbox from any default state"""
        if self.is_selected():
            self.click()
