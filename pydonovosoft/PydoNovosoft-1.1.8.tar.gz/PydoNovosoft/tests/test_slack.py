from unittest import TestCase
import PydoNovosoft


class TestSlack(TestCase):

    def test_class(self):
        slack = PydoNovosoft.Slack('')
        self.assertTrue(slack is not None)

    def test_post(self):
        slack = PydoNovosoft.Slack('')
        message = dict()
        message["user"] = "Bot"
        message["text"] = "Ejemplo de como envio mensajes de manera automatica"
        ret = slack.post("monitoring", message)
        print(ret)
        self.assertTrue(ret is not None)

    def test_attachments(self):
        slack = PydoNovosoft.Slack('')
        attachs = {"username": "Altotrack", "color": "danger", "fallback": "", "fields": [{
            "title": "Esto es una prueba",
            "value": "*No se puede poner caracteres especiales*"
        }]}
        attachments = [attachs]
        message = dict()
        message["user"] = "Altotrack"
        message["text"] = ""
        ret = slack.post_attachments("monitoring", message, attachments)
        self.assertTrue(ret is not None)

