
import random

from promium.base import Element
from promium.base import Sequence
from promium.exceptions import PromiumException


class RadioButton(Element):

    def select(self):
        """Selects radio button"""
        if not self.is_selected():
            self.click()
        else:
            pass

    def select_random_button(self):
        """Selects random radio button from list"""
        if isinstance(self, Sequence):
            random.random(self).select()
        else:
            raise PromiumException("Element is not a list.")

    def is_one_button_already_selected(self):
        """Checks is one button from list already selected"""
        if isinstance(self, Sequence):
            return len(
                [button for button in self if button.is_selected()]
            ) == 1
        else:
            raise PromiumException("Element is not a list.")

    @property
    def label(self):
        """Gets label"""
        return self.driver.execute_script(
            """
            element = arguments[0];
            return element.parentElement.innerText;
            """,
            self.lookup()
        )
