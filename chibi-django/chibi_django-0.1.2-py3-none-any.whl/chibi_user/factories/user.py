import factory
from factory import fuzzy
from faker import Factory as Faker_factory

from .token import Token
from chibi_user.models import User as User_model


faker = Faker_factory.create()


class User( factory.DjangoModelFactory ):
    username = factory.LazyAttribute( lambda x: faker.user_name() )
    is_active = fuzzy.FuzzyChoice( [ True, False ] )
    is_staff = fuzzy.FuzzyChoice( [ True, False ] )

    token = factory.RelatedFactory( Token, 'user' )

    class Meta:
        model = User_model
