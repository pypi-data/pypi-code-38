import factory
import hashlib
from .models import Account, ChatProfile
from django.db.models.signals import post_save
from djangoldp.factories import UserFactory

@factory.django.mute_signals(post_save)
class AccountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Account

    user = factory.SubFactory(UserFactory)

    @factory.post_generation
    def members(self, create, extracted, **kwargs):
        if not create:
            return

        emailMd5 = hashlib.md5(self.user.email.encode('utf-8')).hexdigest()
        self.picture = "https://www.gravatar.com/avatar/%s" % emailMd5
        self.save()

@factory.django.mute_signals(post_save)
class ChatProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ChatProfile

    user = factory.SubFactory(UserFactory)
    jabberID = factory.Faker('email')

