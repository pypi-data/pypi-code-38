import factory
from django.conf import settings

from .models import Circle
from django.db.models.signals import post_save


@factory.django.mute_signals(post_save)
class CircleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Circle

    name = factory.Faker('word')
    description = factory.Faker('text', max_nb_chars=250)
    owner = factory.Iterator(settings.AUTH_USER_MODEL.objects.all())
    jabberID = factory.Faker('email')
    jabberRoom = True


    @factory.post_generation
    def members(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for member in extracted:
                self.team.add(member)
