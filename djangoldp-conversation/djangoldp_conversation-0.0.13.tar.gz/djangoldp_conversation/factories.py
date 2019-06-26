import factory
from .models import Conversation, Message
from django.contrib.auth.models import User
from django.db.models.signals import post_save

@factory.django.mute_signals(post_save)
class ConversationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Conversation

    title = factory.Faker('text', max_nb_chars=250)
    text = factory.Faker('paragraph', nb_sentences=3, variable_nb_sentences=True)
    author_user = factory.Iterator(User.objects.all())
    dateCreated = factory.Faker('past_datetime')


@factory.django.mute_signals(post_save)
class MessageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Message

    conversation = factory.SubFactory(ConversationFactory)
    text = factory.Faker('paragraph', nb_sentences=3, variable_nb_sentences=True)
    author_user = factory.Iterator(User.objects.all())
    dateCreated = factory.Faker('past_datetime')
