from metagenomi.tasks.taskbase import MgTask
from metagenomi.helpers import to_decimal


class Nonpareil(MgTask):
    def __init__(self, mgid, **data):
        MgTask.__init__(self, mgid,  **data)

        self.c = to_decimal(self.d.get('c', 'None'))
        self.diversity = to_decimal(self.d.get('diversity', 'None'))
        self.input = self.d.get('input', 'None')
        self.kappa = self.d.get('kappa', 'None')
        self.lr = self.d.get('lr', 'None')
        self.lr_star = to_decimal(self.d.get('lr_star', 'None'))
        self.modelr = to_decimal(self.d.get('modelr', 'None'))
        self.output = self.d.get('output', 'None')
        self.pdf = self.d.get('pdf', 'None')
        self.tsv = self.d.get('tsv', 'None')

        self.schema = {**self.schema, **{
            'c': {'required': True, 'type': 'decimal'},
            'diversity': {'required': True, 'type': 'decimal'},
            'input': {'required': True, 'type': 's3file'},
            'kappa': {'required': True, 'type': 'decimal'},
            'lr': {'required': True, 'type': 'decimal'},
            'lr_star': {'required': True, 'type': 'decimal'},
            'modelr': {'required': True, 'type': 'decimal'},
            'output': {'required': True, 'type': 's3path'},
            'pdf': {'required': True, 'type': 's3file'},
            'tsv': {'required': True, 'type': 's3file'}
        }}

        if self.check:
            self.validate()

    # def write(self):
    #     '''
    #     fill in
    #     '''
    #     # TODO: audra?
    #     key = 'nonpareil_metadata'
    #     value = self.to_dict()
    #
    #     self.write_new(key, value)
