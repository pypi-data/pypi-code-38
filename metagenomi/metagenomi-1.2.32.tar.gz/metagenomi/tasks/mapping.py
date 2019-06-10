from metagenomi.tasks.taskbase import MgTask
from metagenomi.helpers import to_decimal
from metagenomi.helpers import to_int


class Mapping(MgTask):
    def __init__(self, mgid, **data):
        if not len(data):
            raise ValueError('Cannot initialize a mapping with no data')

        MgTask.__init__(self, mgid, **data)

        self.aligned_mapq_greaterequal_10 = to_int(self.d.get(
                                                'aligned_mapq_greaterequal_10',
                                                'None'))
        self.aligned_mapq_less_10 = to_int(self.d.get('aligned_mapq_less_10',
                                                    'None'))
        self.percent_pairs = to_decimal(self.d.get('percent_pairs', 'None'))
        self.reads_per_sec = to_int(self.d.get('reads_per_sec', 'None'))
        self.seed_size = to_int(self.d.get('seed_size', 'None'))
        self.time_in_aligner_seconds = to_int(self.d.get(
                                        'time_in_aligner_seconds', 'None'))

        self.too_short_or_too_many_nns = to_int(self.d.get(
                                            'too_short_or_too_many_nns',
                                            'None'))
        self.total_bases = to_int(self.d.get('total_bases', 'None'))
        self.total_reads = to_int(self.d.get('total_reads', 'None'))
        self.unaligned = to_int(self.d.get('unaligned', 'None'))
        self.paired = self.d.get('paired', True)
        self.reads_mapped = self.d.get('reads_mapped', 'None')

        self.reference = str(self.d.get('reference', 'None'))
        self.output = str(self.d.get('output', 'None'))

        self.self_mapping = self.d.get('self_mapping')
        self.associated_mapping = self.d.get('associated_mapping')

        self.name = self.d.get('name')

        self.unique_id = self.d.get('unique_id')

        self.schema = {**self.schema, **{
            'aligned_mapq_greaterequal_10': {
                'required': True, 'type': 'integer'},
            'aligned_mapq_less_10': {'required': True, 'type': 'integer'},
            'percent_pairs': {'required': True, 'type': 'decimal'},
            'reads_per_sec': {'required': True, 'type': 'integer'},
            'seed_size': {'required': True, 'type': 'integer'},
            'time_in_aligner_seconds': {'required': True, 'type': 'integer'},
            'too_short_or_too_many_nns': {'required': True, 'type': 'integer'},
            'total_bases': {'required': True, 'type': 'integer'},
            'total_reads': {'required': True, 'type': 'integer'},
            'unaligned': {'required': True, 'type': 'integer'},
            'paired': {'required': True, 'type': 'boolean'},
            'reads_mapped': {'required': True,
                             'type': 'list',
                             'schema': {'type': 's3file'}},
            'reference': {'required': True, 'type': 's3file'},
            'output': {'required': True, 'type': 's3file'},
            'self_mapping': {'required': True, 'type': 'boolean'},
            'associated_mapping': {'required': True, 'type': 'boolean'},
            'name': {'required': True, 'type': 'string'},
            # bc it is None when an object is initialized.
            # Only populated when written.
            'unique_id': {'type': 'decimal', 'nullable': True}
        }}

        if self.check:
            self.validate()

    def delete(self):
        self._delete_from_list(self.whoami(), self.unique_id)

    def write(self):
        '''
        Create new Mapping entry
        '''

        if self.unique_id is None:
            self._update(self.whoami(), self.to_dict(validate=True, clean=True))
        else:
            self._overwrite(self.whoami(), self.to_dict(validate=True, clean=True), self.unique_id)

    def set_output(self, output, write=True):
        self.output = output
        if write:
            if self.validate():
                self.write()

    def whoami(self):
        return('Mappings')
