from fbchat.models import *
from fbchat import Client


class fbnotify:
    def __init__(self, email, password):
        self.client = Client(email, password)

    def send(self, message):
        self.client.send(Message(text=message), thread_id=self.client.uid, thread_type=ThreadType.USER)


#fbnotify('kshr2d2@gmail.com', 'Kshr2d2@01121&').send('hi')
