import factory

from metagenomi.models.assembly import Assembly

from tests.factories.mapping_factory import MappingFactory
from tests.factories.assembly_stats_factory import Assembly_statsFactory


class AssemblyFactory(factory.Factory):
    mgid = factory.Faker('word')
    mgtype = 'assembly'
    Mapping = factory.List([
        factory.SubFactory(MappingFactory),
    ])
    megahit = factory.SubFactory(Assembly_statsFactory)

    class Meta:
        model = Assembly
