from metagenomi.tasks.taskbase import MgTask
from metagenomi.helpers import to_int


class CrisprConnection(MgTask):
    def __init__(self, mgid, **data):
        if not len(data):
            raise ValueError('Cannot initialize a CrispConnection with no data')

        MgTask.__init__(self, mgid, **data)
        self.total_hits = to_int(self.d.get('total_hits'))
        self.total_spacers_w_targets = to_int(self.d.get('total_spacers_w_targets'))
        self.total_target_contigs = to_int(self.d.get('total_target_contigs'))

        self.protospacer_hits = self.d.get('protospacer_hits', 'None')
        self.database_contigs = self.d.get('database_contigs', 'None')
        self.name = self.d.get('name')
        self.unique_id = self.d.get('unique_id')

        self.schema = {**self.schema, **{
            'total_hits': {'required': True, 'type': 'integer'},
            'total_spacers_w_targets': {'required': True, 'type': 'integer'},
            'total_target_contigs': {'required': True, 'type': 'integer'},
            'protospacer_hits': {'required': True, 'type': 's3file'},
            'database_contigs': {'required': True,
                                 'type': 'list',
                                 'schema': {'type': 's3file'}},
            'name': {'required': True, 'type': 'string'},
            # bc it is None when an object is initialized.
            # Only populated when written.
            'unique_id': {'type': 'decimal', 'nullable': True}
            }
        }

        if self.check:
            self.validate()

    def download_protospacer_hits(overwrite=True)

    def delete(self):
        self._delete_from_list(self.whoami(), self.unique_id)

    def write(self):
        '''
        Create new CX entry
        '''
        if self.unique_id is None:
            self._update(self.whoami(), self.to_dict(validate=True, clean=True))
        else:
            self._overwrite(self.whoami(), self.to_dict(validate=True, clean=True), self.unique_id)

    def whoami(self):
        return('CrisprConnections')

    def download_protospacer_hits(self, dir_to_dl=os.getcwd(), overwrite=False, dry_run=False):
        return download_file(self.protospacer_hits, dir_to_dl, dry_run=dry_run, overwrite=overwrite)

    def download_database_contigs(self, dir_to_dl=os.getcwd(), overwrite=False, dry_run=False):
        local_dbs = []
        for file in self.database_contigs:
            local_file = download_file(file, dir_to_dl, dry_run=dry_run, overwrite=overwrite)
            local_dbs.append(local_file)
