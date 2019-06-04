from cortex import Message

from .fixtures import john_doe_token

def test_Message_with_payload():
    m = Message.with_payload({'foo': 'bar'}, token=john_doe_token())
    assert isinstance(m, Message)