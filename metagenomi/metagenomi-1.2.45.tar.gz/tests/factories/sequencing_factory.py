import factory

from metagenomi.models.sequencing import Sequencing

from tests.factories.cleaning_factory import CleaningFactory


class SequencingFactory(factory.Factory):
    mgid = factory.Faker('word')
    Cleaning = factory.SubFactory(CleaningFactory)
    # SequencingInfo = factory.Faker('random_sequencing_info')

    class Meta:
        model = Sequencing
