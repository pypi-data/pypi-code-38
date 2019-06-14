
from promium.exceptions import PromiumException


class BaseElementConditionWithRefresh(object):

    def __init__(self, element, with_refresh=False):
        self.element = element
        self.with_refresh = with_refresh

    def call_method(self):
        raise PromiumException('Not implemented')

    def __call__(self, driver):
        if self.with_refresh:
            driver.refresh()
        return self.call_method()


class ElementPresent(BaseElementConditionWithRefresh):

    def call_method(self):
        return bool(self.element.is_present())


is_present = ElementPresent


class ElementNotPresent(BaseElementConditionWithRefresh):

    def call_method(self):
        return bool(not self.element.is_present())


is_not_present = ElementNotPresent


class ElementIsDisplay(BaseElementConditionWithRefresh):

    def call_method(self):
        return bool(self.element.is_displayed())


is_display = ElementIsDisplay


class ElementNotDisplay(BaseElementConditionWithRefresh):

    def call_method(self):
        return bool(not self.element.is_displayed())


is_not_display = ElementNotDisplay


class ElementText(BaseElementConditionWithRefresh):

    def __init__(self, element, text, with_refresh=False):
        super(ElementText, self).__init__(element, with_refresh)
        self.text = text

    def call_method(self):
        return bool(self.element.text == self.text)


is_text = ElementText


class ElementTextContain(ElementText):

    def call_method(self):
        return bool(self.text in self.element.text)


is_text_contain = ElementTextContain


class ElementTextNotContain(ElementText):

    def bool_method(self):
        return bool(self.text not in self.element.text)


is_text_not_contain = ElementTextNotContain
