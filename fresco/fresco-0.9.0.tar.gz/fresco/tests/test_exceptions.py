from fresco import FrescoApp, GET
from fresco.exceptions import BadRequest, RedirectTemporary


class TestResponseExceptions(object):

    def test_exception_is_converted_to_response(self):

        def redirector():
            raise RedirectTemporary('/foo')

        app = FrescoApp()
        app.route('/', GET, redirector)

        with app.requestcontext('/'):
            assert app.view().status_code == 302

    def test_exception_can_have_its_response_modified(self):

        def view():
            raise BadRequest(content='custom error message',
                             content_type='application/foo')

        app = FrescoApp()
        app.route('/', GET, view)

        with app.requestcontext('/'):
            response = app.view()
            assert response.status_code == 400
            assert ''.join(response.content) == 'custom error message'
            assert response.get_header('Content-Type') == 'application/foo'
