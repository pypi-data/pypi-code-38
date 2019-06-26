from ftw.testbrowser import browser


class LanguageSwitcher():

    @property
    def available(self):
        return bool(browser.css('#portal-languageselector'))

    @property
    def current(self):
        return browser.css(
            '#portal-languageselector .actionMenuHeader a').first.text

    @property
    def language_links(self):
        return browser.css('#portal-languageselector .actionMenuContent a')

    @property
    def languages(self, sort=False):
        return self.language_links.text

    def click_language(self, label):
        browser.find_link_by_text(label).click()
        return self

    def visit(self, obj):
        browser.visit(obj)
        return self

    def visit_portal(self):
        browser.visit()
        return self
