from pytest_bdd import when, then
from pytest_bdd import parsers
from splinter.driver.webdriver import BaseWebDriver


@then(
    parsers.re(
        r'the checkbox "(?P<checkbox>(?:\\.|[^"\\])*)" is (?P<state>not checked|checked)$'
    )
)
def checkbox_state(browser: BaseWebDriver, checkbox, state):
    elm = browser.find_by_id(checkbox)
    if state == "checked":
        assert elm.checked
    else:
        assert not elm.checked


@when(parsers.parse("I fill in the following:\n{text}"))
def when_fill_multiple_fields(browser: BaseWebDriver, text):
    for line in text.split("\n"):
        field, value = line.split(":", 1)
        browser.fill(field.strip(), value.strip())


@then(
    parsers.re(
        r'the "(?P<field>(?:\\.|[^"\\])*)" field should contain "(?P<value>(?:\\.|[^"\\])*)"$'
    )
)
def then_field_contains(browser: BaseWebDriver, field, value):
    assert browser.find_by_name(field).value == value
