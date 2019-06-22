from pytest_bdd import when, then
from pytest_bdd import parsers
from splinter.driver.webdriver import BaseWebDriver


@when(parsers.re(r'^I see "(?P<text>(?:\\.|[^"\\])*)"'))
def then_text_available(browser: BaseWebDriver, text):
    assert browser.is_text_present(text)


@then(parsers.re(r'^I should see "(?P<text>(?:\\.|[^"\\])*)"'))
def then_text_available(browser: BaseWebDriver, text):
    assert browser.is_text_present(text)


@when(parsers.re(r'^I do not see "(?P<text>(?:\\.|[^"\\])*)"'))
def when_text_not_available(browser: BaseWebDriver, text):
    assert browser.is_text_not_present(text)


@then(parsers.re(r'^I should not see "(?P<text>(?:\\.|[^"\\])*)"'))
def then_text_not_available(browser: BaseWebDriver, text):
    assert browser.is_text_not_present(text)
