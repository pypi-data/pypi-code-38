import factory
from .models import Customer, Project, Member, BusinessProvider
from django.db.models.signals import post_save

@factory.django.mute_signals(post_save)
class CustomerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Customer

    name = factory.Faker('company')
    address = factory.Faker('address')
    logo = factory.Faker('url')
    companyRegister = factory.Faker('random_int', min=0)
    firstName = factory.Faker('first_name')
    lastName = factory.Faker('last_name')
    role = factory.Faker('job')
    email = factory.Faker('email')
    phone = factory.Faker('phone_number')

class BusinessProviderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BusinessProvider

    name = factory.Faker('name')
    fee = factory.Faker('random_int', min=0, max=10)

@factory.django.mute_signals(post_save)
class ProjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Project

    name = factory.Faker('word')
    description = factory.Faker('text', max_nb_chars=250)
    number = factory.Faker('random_int', min=0)
    creationDate = factory.Faker('past_date')
    customer = factory.SubFactory(CustomerFactory)
    businessProvider = factory.SubFactory(BusinessProviderFactory)
    jabberID = factory.Faker('email')
    jabberRoom = True

    @factory.post_generation
    def members(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for member in extracted:
                Member.objects.create(name=factory.Faker('job'), project=self, user=member)
