import sys
import pytest

from metagenomi.models.assembly import Assembly

from tests.factories.assembly_factory import AssemblyFactory


# testing of the Sequencing mgobject


@pytest.fixture()
def setup(request):
    '''Create a basic Sequencing object to test
    '''
    a = AssemblyFactory()
    return(a)

class TestAssemblyCreation(object):
    def test_assembly_creation(self, setup):
        a = setup
        assert a.mgid is not None
