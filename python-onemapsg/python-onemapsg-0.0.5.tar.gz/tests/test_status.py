from onemapsg import status


def test_is_informational():
    assert status.is_informational(100)
    assert status.is_informational(199)
    assert not status.is_informational(99)
    assert not status.is_informational(200)


def test_is_success():
    assert status.is_success(200)
    assert status.is_success(299)
    assert not status.is_success(199)
    assert not status.is_success(300)


def test_is_redirect():
    assert status.is_redirect(300)
    assert status.is_redirect(399)
    assert not status.is_redirect(299)
    assert not status.is_redirect(400)


def test_is_client_error():
    assert status.is_client_error(400)
    assert status.is_client_error(499)
    assert not status.is_client_error(399)
    assert not status.is_client_error(500)


def test_is_server_error():
    assert status.is_server_error(500)
    assert status.is_server_error(599)
    assert not status.is_server_error(499)
    assert not status.is_server_error(600)
