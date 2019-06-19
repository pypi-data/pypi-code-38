import pandas as pd

from metagenomi.tasks.taskbase import MgTask
from metagenomi.helpers import (to_int, to_decimal, to_datetime)


class DNAQuantification(MgTask):
    '''
    RULES
    '''
    def __init__(self, mgid, **data):
        MgTask.__init__(self, mgid, **data)

        self.date = to_datetime(self.d.get('date', 'None'))
        self.sample_name = self.d.get('sample_name', 'None')
        self.nucleic_acid_ng_ul = to_decimal(self.d.get('nucleic_acid_ng_ul', 'None'))
        self.a260_a280 = to_decimal(self.d.get('a260_a280', 'None'))
        self.a260_a230 = to_decimal(self.d.get('a260_a230', 'None'))
        self.a260 = to_decimal(self.d.get('a260', 'None'))
        self.a280 = to_decimal(self.d.get('a280', 'None'))
        self.nucleic_acid_factor = to_int(self.d.get('nucleic_acid_factor', 'None'))
        self.baseline_correction_nm = to_int(self.d.get('baseline_correction_nm', 'None'))
        self.baseline_absorbance = to_decimal(self.d.get('baseline_absorbance', 'None'))

        self.schema = {
            **self.schema, **{
                "date": {"required": True, "type": "datestring"},
                "sample_name": {"required": True, "type": "string"},
                "nucleic_acid_ng_ul": {"required": True, "type": "decimal"},
                "a260_a280": {"required": True, "type": "decimal"},
                "a260_a230": {'required': True, 'type': 'decimal'},
                "a260": {'required': True, 'type': 'decimal'},
                "a280": {'required': True, 'type': 'decimal'},
                "nucleic_acid_factor": {'required': True, 'type': 'integer'},
                "baseline_correction_nm": {'required': True, 'type': 'integer'},
                "baseline_absorbance": {'required': True, 'type': 'decimal'},
            }}

        if self.check:
            self.validate()

    def get_data(self, as_dataframe=True):
        d = {'mgid': [self.mgid],
             'date': [self.date],
             'sample_name': [self.sample_name],
             'nucleic_acid_ng_ul': [self.nucleic_acid_ng_ul],
             'a260_a280': [self.a260_a280],
             'a260_a230': [self.a260_a230],
             'a260': [self.a260],
             'a280': [self.a280],
             'nucleic_acid_factor': [self.nucleic_acid_factor],
             'baseline_correction_nm': [self.baseline_correction_nm]
             }

        if as_dataframe:
            return pd.DataFrame.from_dict(d)
        return d
