import flask

from authutils.user import current_user


def test_set_current_user(app, auth_header, mock_get, claims):
    mock_get()
    with app.test_request_context(path="/test", headers=auth_header):
        assert current_user
        assert hasattr(flask.g, "user")
        assert current_user._claims == claims
