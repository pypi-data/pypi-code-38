import factory
from .models import JobOffer
from django.contrib.auth.models import User
from django.db.models.signals import post_save


@factory.django.mute_signals(post_save)
class JobOfferFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = JobOffer

    author = factory.Iterator(User.objects.all())

    title = factory.Faker('word')
    description = factory.Faker('text', max_nb_chars=250)
    creationDate = factory.Faker('past_date')
    closingDate = factory.Faker('future_date')

    @factory.post_generation
    def skills(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for skill in extracted:
                self.skills.add(skill)
