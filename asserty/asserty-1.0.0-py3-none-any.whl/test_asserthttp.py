from . import assert_that


class MockResponse:
    def __init__(self, status_code: int, body):
        super().__init__()
        self.status_code: int = status_code
        self.body = body

    def json(self) -> dict:
        return self.body
    
    @property
    def text(self):
        return str(self.body)


def test_status():
    res = MockResponse(200, {})
    assert_that(res).has_status_ok()
    assert_that(res).has_status_successful()
    res = MockResponse(201, {})
    assert_that(res).has_status_successful()
    assert_that(res).has_status_created().also.has_status_successful()


def test_body():
    res = MockResponse(200, {"a": 1})
    assert_that(res).body_contains_key("a")
    assert_that(res).body_equals({"a": 1})
    assert_that(res).body_equals("{'a': 1}")


def test_status_and_body():
    res = MockResponse(200, {"a": 1})
    assert_that(res).has_status_ok().also.body_contains_key("a")
