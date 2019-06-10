import os
from metagenomi.models.modelbase import MgModel


# from metagenomi.tasks.cleaning import Cleaning
# from metagenomi.tasks.nonpareil import Nonpareil
from metagenomi.tasks.sequencinginfo import SequencingInfo
from metagenomi.tasks.nonpareil import Nonpareil
from metagenomi.tasks.cleaning import (QualityTrimming, AdapterRemoval, ContaminantRemoval, ReadRepair)
from metagenomi.helpers import download_file


class Sequencing(MgModel):
    # Possible tasks:
    # Nonpareil, Cleaning, sequencingInfo
    # mgtype above MgModel.__init__ because self.mgtype must be referenced
    # for loads based on name string matching
    def __init__(self, mgid, **data):
        self.mgtype = 'sequencing'
        MgModel.__init__(self, mgid, **data)

        self.s3path = self.d.get('s3path')

        if 'mgtype' in self.d:
            self.mgtype = self.d['mgtype']

        self.alt_identifier = self.d.get('alt_identifier')

        self.read_repair = None
        if 'ReadRepair' in self.d:
            self.read_repair = ReadRepair(self.mgid, db=self.db,
                                                    check=self.check,
                                                    **self.d['ReadRepair'])

        self.quality_trimming = None
        if 'QualityTrimming' in self.d:
            self.quality_trimming = QualityTrimming(self.mgid, db=self.db,
                                                    check=self.check,
                                                    **self.d['QualityTrimming'])

        self.adapter_removal = None
        if 'AdapterRemoval' in self.d:
            self.adapter_removal = AdapterRemoval(self.mgid, db=self.db,
                                                  check=self.check,
                                                  **self.d['AdapterRemoval'])

        self.contaminant_removal = None
        if 'ContaminantRemoval' in self.d:
            self.contaminant_removal = ContaminantRemoval(
                                        self.mgid, db=self.db,
                                        check=self.check,
                                        **self.d['ContaminantRemoval'])

        self.sequencing_info = None
        if 'SequencingInfo' in self.d:
            self.sequencing_info = SequencingInfo(self.mgid, db=self.db,
                                                  check=self.check,
                                                  **self.d['SequencingInfo'])

        self.nonpareil = None
        if 'Nonpareil' in self.d:
            self.nonpareil = Nonpareil(self.mgid, db=self.db, check=self.check,
                                       **self.d['Nonpareil'])

        self.schema = {**self.schema, **{
            's3path': {'type': 's3path', 'required': True},
            'ReadRepair': {'type': 'dict'},
            'QualityTrimming': {'type': 'dict'},
            'AdapterRemoval': {'type': 'dict'},
            'ContaminantRemoval': {'type': 'dict'},
            'SequencingInfo': {'type': 'dict'},
            'Nonpareil': {'type': 'dict'},
            'associated': {'type': 'dict', 'required': True, 'schema': {
                'assembly':  {'type': 'list', 'schema': {
                    'type': ['mgid', 'nonestring']}},
                'sample':  {'type': 'list', 'schema': {
                    'type': ['mgid', 'nonestring']}}
                }
            }
        }
        }

        if self.check:
            self.validate()

    def set_s3path(self, newpath, write=True):
        self.s3path = newpath
        if write:
            if self.validate():
                self.update('s3path', newpath)

    def get_cleaned_reads(self, raise_error=True):
        if self.contaminant_removal:
            single = self.contaminant_removal.output.get('single')
            if single is None:
                fwd = self.contaminant_removal.output['fwd']
                rev = self.contaminant_removal.output['rev']
                return [fwd, rev]
            else:
                return [single]
        else:
            if self.adapter_removal:
                single = self.adapter_removal.output.get('single')
                if single is None:
                    fwd = self.adapter_removal.output['fwd']
                    rev = self.adapter_removal.output['rev']
                    return [fwd, rev]
                else:
                    return [single]

        if raise_error:
            e = f'No cleaned reads, bbmap has not been run'
            raise ValueError(e)
        else:
            return None

    def get_raw_reads(self, raise_error=True):
        if self.sequencing_info:
            single = self.sequencing_info.raw_read_paths.get('single')
            if single is None:
                fwd = self.sequencing_info.raw_read_paths['fwd']
                rev = self.sequencing_info.raw_read_paths['rev']
                return [fwd, rev]
            else:
                return [single]

    def download_reads(self, cleaned=True, dir_to_dl=os.getcwd()):
        if cleaned:
            reads = self.get_cleaned_reads()
        else:
            reads = self.get_raw_reads()

        local_reads = []
        for r in reads:
            local_reads.append(download_file(r, dir_to_dl))
        return local_reads

    def link_sample(self, sample_mgid, xlink=True, write=True):
        '''
        xlink = whether or not you want to also link the corresponding sample
        to this sequencing. If this were always True, would result in infinite
        loop
        '''
        from metagenomi.models.sample import Sample

        if xlink:
            linked_sample = Sample(sample_mgid, db=self.db, load=True)
            linked_sample.link_sequencing(self.mgid, xlink=False)

        if 'sample' in self.associated:
            if self.associated['sample'] == ['None']:
                self.associated['sample'] = [sample_mgid]
            else:
                if sample_mgid not in self.associated['sample']:
                    self.associated['sample'] = self.associated['sample'] + [sample_mgid]
        else:
            self.associated['sample'] = [sample_mgid]
        if write:
            self.write(force=True)

    def link_assembly(self, assembly_mgid, xlink=True, write=True):
        '''
        xlink = whether or not you want to also link the corresponding sample
        to this sequencing. If this were always True, would result in infinite
        loop
        TODO: Allow this to take either an mgid or an object
        '''
        from metagenomi.models.assembly import Assembly
        if xlink:
            linked_assembly = Assembly(assembly_mgid, db=self.db, load=True)
            linked_assembly.link_sequencing(self.mgid, xlink=False)

        if 'assembly' in self.associated:
            if self.associated['assembly'] == ['None']:
                self.associated['assembly'] = [assembly_mgid]
            else:
                if assembly_mgid not in self.associated['assembly']:
                    self.associated['assembly'] = self.associated['assembly'] + [assembly_mgid]
        else:
            self.associated['assembly'] = [assembly_mgid]
        if write:
            self.update('associated', self.associated)

    def get_bbmap_cmd(self, out, bigscratch=False, jobdef='mg-bbmap-jobdef:4'):
        if bigscratch:
            jq = 'mg-data-downloading-jq'
        else:
            jq = 'mg-worker-bulk-jq'
        cmd = f'python submit_bbmap_job.py --mgid {self.mgid} --out {out} --read_repair --job-queue {jq} --job-def {jobdef}'
        return cmd

    def get_redownload_cmd(self, out):
        cmd = f'python submit_data_fetcher_job.py --mgid {self.mgid} --out {out}'
        return cmd

    def get_assembly_cmd(self, out):
        if 'tran' in self.mgid:
            raise ValueError('You are trying to assembly a transcriptome you idiot')

        cmd = f'python submit_megahit_job.py --sequencings {self.mgid} --out {out}'
        return cmd
