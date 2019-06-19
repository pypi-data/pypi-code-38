from metagenomi.tasks.taskbase import MgTask
from metagenomi.helpers import to_int


class CleaningBase(MgTask):
    def __init__(self, mgid, **data):
        MgTask.__init__(self, mgid, **data)
        self.total_removed_reads = to_int(self.d.get('total_removed_reads',
                                                     'None'))
        self.output = self.d.get('output', 'None')

        self.schema = {**self.schema, **{
            'total_removed_reads': {'type': 'integer', 'required': True}
        }}

        if 'rev' in self.output:
            self.schema = {**self.schema, **{
                'output': {'type': 'dict', 'required': True, 'schema': {
                    'fwd': {'type': 's3file', 'required': True},
                    'rev': {'type': 's3file', 'required': True}}
                    }}}
        else:
            self.schema = {**self.schema, **{
                'output': {'type': 'dict', 'required': True, 'schema': {
                    'single': {'type': 's3file', 'required': True}}
                    }}}


class QualityTrimming(CleaningBase):
    def __init__(self, mgid, **data):
        CleaningBase.__init__(self, mgid, **data)

        if self.check:
            self.validate()


class AdapterRemoval(CleaningBase):
    def __init__(self, mgid, **data):
        CleaningBase.__init__(self, mgid, **data)
        self.ftrimmed_reads = to_int(self.d.get('ftrimmed_reads', 'None'))
        self.ktrimmed_reads = to_int(self.d.get('ktrimmed_reads', 'None'))
        self.trimmed_by_overlap_reads = to_int(self.d.get(
                                'trimmed_by_overlap_reads', 'None'))

        self.schema = {**self.schema, **{
            'ftrimmed_reads': {'type': 'integer', 'required': True},
            'ktrimmed_reads': {'type': 'integer', 'required': True},
            'trimmed_by_overlap_reads': {'type': 'integer', 'required': True}
        }}

        if self.check:
            self.validate()


class ContaminantRemoval(CleaningBase):
    def __init__(self, mgid, **data):
        CleaningBase.__init__(self, mgid, **data)
        if self.check:
            self.validate()


class ReadRepair(CleaningBase):
    def __init__(self, mgid, **data):
        CleaningBase.__init__(self, mgid, **data)
        self.input_reads = to_int(self.d.get('input_reads', 'None'))
        self.input_bases = self.d.get('input_bases')
        self.paired_reads = to_int(self.d.get('paired_reads', 'None'))
        self.singleton_reads = to_int(self.d.get(
                                'singleton_reads', 'None'))

        self.schema = {**self.schema, **{
            'output': {'type': ['s3file', 'nonestring'], 'required': True},
            'input_reads': {'type': 'integer', 'required': True},
            'input_bases': {'type': 'integer'},
            'paired_reads': {'type': 'integer', 'required': True},
            'singleton_reads': {'type': 'integer', 'required': True},
        }}
        if self.check:
            self.validate()
