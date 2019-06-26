from django.conf import settings
from django.db import models
from djangoldp.models import Model


class Conversation(Model):
    title = models.TextField()
    text = models.TextField(null=True)
    author_user = models.ForeignKey(settings.AUTH_USER_MODEL)
    dateCreated = models.DateTimeField(auto_now_add=True)

    class Meta:
        permissions = (
            ('view_conversation', 'Read'),
            ('control_conversation', 'Control'),
        )
        auto_author = 'author_user'
        ordering = ['-dateCreated']
        container_path = "conversations"
        nested_fields = ["message_set", "author_user"]
        rdf_type = 'hd:conversation'

    def __str__(self):
        return '{}'.format(self.title)


class Message(Model):
    dateCreated = models.DateField(auto_now_add=True)
    text = models.TextField()
    conversation = models.ForeignKey("Conversation", on_delete=models.DO_NOTHING)
    author_user = models.ForeignKey(settings.AUTH_USER_MODEL)

    # response_to = models.ForeignKey(Member, on_delete=models.SET_NULL, related_name="response", blank=True, null=True)

    class Meta:
        permissions = (
            ('view_message', 'Read'),
            ('control_message', 'Control'),
        )
        auto_author = 'author_user'
        ordering = ['dateCreated']
        container_path = "messages"
        nested_fields = ["author_user"]
        rdf_type = 'hd:conversationmessage'
        depth = 0

    def __str__(self):
        return '{}, le {}'.format(self.text, self.dateCreated)
