from metagenomi.tasks.taskbase import MgTask
from metagenomi.helpers import to_int


class Prodigal(MgTask):
    '''
    RULES
    '''
    def __init__(self, mgid, **data):
        MgTask.__init__(self, mgid, **data)
        # self.key = 'prodigal_metadata'

        self.proteins_predicted = to_int(self.d.get('proteins_predicted', 'None'))
        self.min_sequence_length = to_int(self.d.get('min_sequence_length', 'None'))
        self.contigs_above_cutoff = to_int(self.d.get('contigs_above_cutoff', 'None'))
        self.contigs_below_cutoff = to_int(self.d.get('contigs_below_cutoff', 'None'))
        self.mode = self.d.get('mode', 'None')
        self.protein_file = self.d.get('protein_file', 'None')
        self.pullseq_contigs = self.d.get('pullseq_contigs', 'None')

        self.schema = {
            **self.schema, **{
                "proteins_predicted": {"required": True, "type": "integer"},
                "min_sequence_length": {"required": True, "type": "integer"},
                "contigs_above_cutoff": {"required": True, "type": "integer"},
                "contigs_below_cutoff": {"required": True, "type": "integer"},
                "pullseq_contigs": {'required': True, 'type': 's3file'},
                "mode": {'required': True,
                         'type': 'string',
                         'allowed': ['single', 'meta']
                         }
                    },
                "protein_file": {'required': True, 'type': 's3file'}
            }

        if self.check:
            self.validate()
