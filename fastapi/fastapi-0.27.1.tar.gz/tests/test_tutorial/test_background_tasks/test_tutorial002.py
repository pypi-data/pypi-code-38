import os
from pathlib import Path

from starlette.testclient import TestClient

from background_tasks.tutorial002 import app

client = TestClient(app)


def test():
    log = Path("log.txt")
    if log.is_file():
        os.remove(log)  # pragma: no cover
    response = client.post("/send-notification/foo@example.com?q=some-query")
    assert response.status_code == 200
    assert response.json() == {"message": "Message sent"}
    with open("./log.txt") as f:
        assert "found query: some-query\nmessage to foo@example.com" in f.read()
