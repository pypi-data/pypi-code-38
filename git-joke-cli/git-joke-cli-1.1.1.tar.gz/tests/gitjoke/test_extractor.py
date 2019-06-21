import responses

from gitjoke.extractor import get_joke, get_jokes


def stub_request():
    def request_callback(request):
        body = 'foo\nbar\n'
        return (200, {}, body)

    url = 'https://raw.githubusercontent.com/EugeneKay/git-jokes/lulz/Jokes.txt'  # noqa: E501
    responses.add_callback(responses.GET, url, callback=request_callback)


@responses.activate
def test_get_jokes():
    stub_request()
    jokes = get_jokes()
    assert jokes == ['foo', 'bar']


@responses.activate
def test_get_joke():
    stub_request()
    joke = get_joke()
    assert joke in ['foo', 'bar']
