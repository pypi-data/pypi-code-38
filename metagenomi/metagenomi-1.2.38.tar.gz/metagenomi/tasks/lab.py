
from metagenomi.tasks.taskbase import MgTask
from metagenomi.helpers import (to_int, to_decimal, to_datetime)


class Lab(MgTask):
    '''
    TODO: write me
    '''
    def __init__(self, mgid, **data):
        MgTask.__init__(self, mgid, **data)

        # REQUIRED
        self.extracted_on = to_datetime(self.d.get('extracted_on', 'None'))
        self.kit_used = self.d.get('kit_used', 'None')
        self.dna_quantification = to_decimal(self.d.get('dna_quantification', 'None'))
        self.rna_quantification = to_decimal(self.d.get('rna_quantification', 'None'))
        self.extracted_by = self.d.get('extracted_by', 'None')
        self.tube_lable = self.d.get('tube_lable', 'None')

        self.notes = self.d.get('notes', 'None')
        self.storage_location = self.d.get('storage_location', 'None')

        # TODO: make it pull this from **data
        self.extra_metadata = {k: v for k, v in self.d.items()
                               if k not in self.__dict__.keys()}

        self.schema = {**self.schema, **{
            'extracted_on': {
                'required': True, 'type': ['datestring', 'nonestring']},
            'kit_used': {
                'required': True, 'type': 'string'},
            'dna_quantification': {
                'required': True, 'type': ['decimal', 'Nonestring']},
            'rna_quantification': {
                'required': True, 'type': ['decimal', 'Nonestring']},
            'extracted_by': {
                'required': True, 'type': 'string'},
            'tube_lable': {
                'required': True, 'type': 'string'},
            'notes': {
                'required': True, 'type': 'string'},
            'storage_location': {
                'required': True, 'type': 'string'},
            'extra_metadata': {
                'required': False, 'type': 'dict'}
            }
        }

        if self.check:
            self.validate()
