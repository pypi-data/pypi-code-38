from metagenomi.models.modelbase import MgModel


from metagenomi.tasks.sampleinfo import SampleInfo
# from metagenomi.tasks.lab import Lab
from metagenomi.tasks.dna_quantification import DNAQuantification


class Sample(MgModel):
    # Possible tasks:
    def __init__(self, mgid, **data):
        self.mgtype = 'sample'
        MgModel.__init__(self, mgid, **data)

        if 'mgtype' in self.d:
            self.mgtype = self.d['mgtype']

        self.environment = self.d.get('environment', 'None').rstrip()

        self.sample_info = None
        if 'SampleInfo' in self.d:
            self.sample_info = SampleInfo(
                                    self.mgid, db=self.db, check=self.check,
                                    **self.d['SampleInfo']
                                    )

        self.dna_quantification = None
        if 'DNAQuantification' in self.d:
            self.dna_quantification = DNAQuantification(self.mgid, db=self.db,
                                          check=self.check,
                                          **self.d['DNAQuantification'])

        # TODO: Think about this more and implement
        # self.lab = None
        # if 'Lab' in self.d:
        #     self.lab = Lab(self.mgid, db=self.db, check=self.check, **self.d['Lab'])

        self.schema = {**self.schema, **{
            'SampleInfo': {'type': 'dict'},
            'DNAQuantification': {'type': 'dict'},
            'associated': {'type': 'dict', 'required': True, 'schema': {
                'sequencing': {'type': 'list', 'schema': {
                    'type': ['mgid', 'nonestring']}}
                }},
            'environment': {
                'type': 'string', 'required': True,
                'allowed': [
                            'Soil',
                            'Thermophilic',
                            'Ocean',
                            'Fresh water',
                            'Human stool',
                            'Human saliva',
                            'Human other',
                            'Salt-water associated sediment',
                            'Fresh-water associated sediment',
                            'Non-human stool',
                            'Non-human other'
                            ]}}}

        if self.check:
            self.validate()

    def set_environment(self, environment, write=True):
        self.environment = environment
        if write:
            self.write(force=True)

    def link_sequencing(self, seq_mgid, xlink=True, write=True):
        '''
        TODO: Allow this to take either an mgid or an object
        '''
        from metagenomi.models.sequencing import Sequencing
        if xlink:
            linked_sequencing = Sequencing(seq_mgid, db=self.db, load=True)
            linked_sequencing.link_sample(self.mgid)

        if 'sequencing' in self.associated:
            if self.associated['sequencing'] == ['None']:
                self.associated['sequencing'] = [seq_mgid]
            else:
                if seq_mgid not in self.associated['sequencing']:
                    self.associated['sequencing'] = self.associated['sequencing'] + [seq_mgid]
        else:
            self.associated['sequencing'] = [seq_mgid]

        if write:
            self.update('associated', self.associated)

    def get_coassembly_cmd(self):
        sequencings = [i for i in self.associated['sequencing'] if 'tran' not in i and i != 'None']
        if len(sequencings) > 0:
            cmd = f'python submit_megahit_job.py --sequencings {" ".join(sequencings)}'
            return cmd
        return
