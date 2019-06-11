import sys
import pytest

from metagenomi.models.sequencing import Sequencing

from tests.factories.sequencing_factory import SequencingFactory

from moto import mock_dynamodb2


# testing of the Sequencing mgobject


@pytest.fixture()
def setup(request):
    '''Create a basic Sequencing object to test
    '''
    s = SequencingFactory()
    return(s)

class TestSequencingCreation(object):
    def test_sequencing_creation(self, setup):
        s = setup
        assert s.mgid is not None
        assert s.cleaning.total_reads > 0
        assert s.cleaning.total_bases > 0
        assert s.cleaning is not None
        assert s.cleaning.adapter_removal.total_removed_reads > 0
        assert s.cleaning.adapter_removal.trimmed_by_overlap_reads > 0
        assert s.cleaning.adapter_removal.ftrimmed_reads > 0
        assert s.cleaning.adapter_removal.ktrimmed_reads > 0
        assert s.cleaning.adapter_removal.cmd_run.startswith('/tmp/bbmap/bbduk.sh')
        assert s.cleaning.contaminant_removal is not None
        assert s.cleaning.contaminant_removal.total_removed_reads > 0
        assert s.cleaning.contaminant_removal.contaminants > 0
        assert s.cleaning.contaminant_removal.cmd_run.startswith('/tmp/bbmap/bbduk.sh')
        assert s.cleaning.quality_trimming is not None
        assert s.cleaning.quality_trimming.total_removed_reads > 0
        assert s.cleaning.contaminant_removal.cmd_run.startswith('/tmp/bbmap/bbduk.sh')


class TestSequencingUpdate(object):
    pass
