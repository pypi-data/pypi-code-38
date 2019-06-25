from cifsdk.client.ws import DefaultHandler


def test_ws():
    class MyHandler(DefaultHandler):
        def on_close(self, ws):
            ws.close()

    h = MyHandler(token='1234')
    assert h
