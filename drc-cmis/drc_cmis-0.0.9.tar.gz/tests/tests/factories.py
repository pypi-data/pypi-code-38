from uuid import uuid4

import factory
from faker import Faker

fake = Faker()


class EnkelvoudigInformatieObjectFactory(factory.DjangoModelFactory):
    identificatie = factory.Sequence(lambda a: uuid4())
    bronorganisatie = factory.Sequence(lambda x: '1234{}'.format(x))
    creatiedatum = factory.Faker('date')
    titel = factory.Faker('word')
    vertrouwelijkheidaanduiding = factory.Faker('word')
    auteur = factory.Faker('first_name')
    formaat = 'some formaat'
    taal = 'dut'
    beschrijving = factory.Faker('paragraph')
    inhoud = factory.django.FileField(data=fake.word().encode('utf-8'), filename=fake.file_name())
    informatieobjecttype = 'https://example.com/ztc/api/v1/catalogus/1/informatieobjecttype/1'

    class Meta:
        model = 'app.EnkelvoudigInformatieObject'
