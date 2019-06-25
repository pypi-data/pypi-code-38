from metagenomi.tasks.taskbase import MgTask
from metagenomi.helpers import to_int


class R16S(MgTask):
    def __init__(self, mgid, **data):
        MgTask.__init__(self, mgid,  **data)

        self.num_16s = to_int(self.d.get('num_16s', 'None'))
        self.domains = self.d.get('domains', 'None')
        self.insertions = to_int(self.d.get('insertions', 'None'))
        self.output = self.d.get('output', 'None')

        self.schema = {**self.schema, **{
            'num_16s': {'required': True, 'type': 'integer'},
            'output': {'required': True, 'type': 's3path'},
            'domains': {'required': True, 'type': 'dict'},
            'insertions': {'required': True, 'type': 'integer'}
        }}

        if self.check:
            self.validate()
