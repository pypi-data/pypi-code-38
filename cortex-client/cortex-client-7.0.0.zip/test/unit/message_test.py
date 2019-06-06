from cortex import Message

def test_Message_with_payload():
    m = Message.with_payload({'foo': 'bar'})
    assert isinstance(m, Message)

