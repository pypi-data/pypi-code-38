import mywebapp.webapp

def test_api():
    api = mywebapp.webapp.API()
    assert api.message == "Hello, World"

