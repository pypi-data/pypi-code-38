from metagenomi.tasks.taskbase import MgTask
from metagenomi.helpers import to_int


class JgiMetadata(MgTask):
    '''
    TODO: write me
    '''
    def __init__(self, mgid, **data):
        MgTask.__init__(self, mgid, **data)

        self.project_name = self.d.get('project_name', 'None')
        self.principal_investigator = self.d.get('principal_investigator',
                                                 'None')
        self.scientific_program = self.d.get('scientific_program', 'None')
        self.product_name = self.d.get('product_name', 'None')
        self.status = self.d.get('status', 'None')
        self.status_date = self.d.get('status_date', 'None')
        self.user_program = self.d.get('user_program', 'None')
        self.proposal = self.d.get('proposal', 'None')

        self.jgi_project_id = to_int(self.d.get('jgi_project_id', 'None'))
        self.taxonomy_id = to_int(self.d.get('taxonomy_id', 'None'))
        self.ncbi_project_id = to_int(self.d.get('ncbi_project_id', 'None'))
        self.sequencing_project_id = to_int(self.d.get(
                                        'sequencing_project_id', 'None'))
        self.analysis_project_id = to_int(self.d.get('analysis_project_id',
                                                     'None'))

        self.genbank = self.d.get('genbank', 'None')

        self.ena = self.d.get('ena', 'None')
        self.sra = self.d.get('sra', 'None')

        self.project_manager = self.d.get('project_manager', 'None')
        self.portal_id = self.d.get('portal_id', 'None')
        self.img_portal = self.d.get('img_portal', 'None')

        self.schema = {**self.schema, **{
            "project_name": {
                'required': True, 'type': 'string', 'minlength': 1},
            "principal_investigator": {
                'required': True, 'type': 'string', 'minlength': 1},
            "scientific_program": {
                'required': True, 'type': 'string', 'minlength': 1},
            "product_name": {
                'required': True, 'type': 'string', 'minlength': 1},
            "status": {
                'required': True, 'type': 'string', 'minlength': 1},
            "status_date": {
                'required': True, 'type': 'string', 'minlength': 1},
            "user_program": {
                'required': True, 'type': 'string', 'minlength': 1},
            "proposal": {
                'required': True, 'type': 'string', 'minlength': 1},
            "jgi_project_id": {'required': True,
                               'type': ['integer', 'nonestring']},
            "taxonomy_id": {'required': True,
                            'type': ['integer', 'nonestring']},
            "ncbi_project_id": {'required': True,
                                'type': ['integer', 'nonestring']},
            "sequencing_project_id": {'required': True,
                                      'type': ['integer', 'nonestring']},
            "analysis_project_id": {'required': True,
                                    'type': ['integer', 'nonestring']},
            "genbank": {'required': True, 'type': 'string', 'minlength': 1},
            "ena": {'required': True, 'type': 'string', 'minlength': 1},
            "sra": {'required': True, 'type': 'string', 'minlength': 1},
            "project_manager": {
                'required': True, 'type': 'string', 'minlength': 1},
            "portal_id": {
                'required': True, 'type': 'string', 'minlength': 1},
            "img_portal": {
                'required': True, 'type': 'string', 'minlength': 1}
            }
        }

        if self.check:
            self.validate()
