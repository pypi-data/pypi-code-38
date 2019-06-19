from metagenomi.tasks.taskbase import MgTask
from metagenomi.helpers import to_int


class HmmSearch(MgTask):
    def __init__(self, mgid, **data):
        if not len(data):
            raise ValueError('Cannot initialize an hmm search with no data')
        MgTask.__init__(self, mgid, **data)

        self.hmm_db = self.d.get('hmm_db')
        self.num_hits = to_int(self.d.get('num_hits'))
        self.type = self.d.get('type')
        self.output = self.d.get('output')
        self.name = self.d.get('name')
        self.unique_id = self.d.get('unique_id')

        self.schema = {**self.schema, **{
            'hmm_db': {'required': True, 'type': 's3file'},
            'num_hits': {'required': True, 'type': 'integer'},
            'type': {'required': True, 'type': 'string'},
            'output': {'required': True, 'type': 's3file'},
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
        Create new HmmSearch entry
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
        return('HmmSearches')
