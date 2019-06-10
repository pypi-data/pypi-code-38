import os

from metagenomi.models.modelbase import MgModel

from metagenomi.tasks.assemblystats import AssemblyStats
from metagenomi.tasks.prodigal import Prodigal
from metagenomi.tasks.mapping import Mapping
from metagenomi.tasks.minced import Minced
from metagenomi.tasks.crisprconnection import CrisprConnection
from metagenomi.tasks.hmm import HmmSearch
from metagenomi.tasks.jgimetadata import JgiMetadata
from metagenomi.helpers import download_file

# from metagenomi.logger import logger


class Assembly(MgModel):
    # Possible tasks:
    # Mapping, Megahit, TODO:Prodigal
    def __init__(self, mgid, **data):
        self.mgtype = 'assembly'
        MgModel.__init__(self, mgid, **data)

        self.s3path = self.d.get('s3path')

        if 'mgtype' in self.d:
            self.mgtype = self.d['mgtype']

        self.mappings = None
        if 'Mappings' in self.d:
            self.mappings = []
            for m in self.d['Mappings']:
                self.mappings.append(Mapping(self.mgid, db=self.db, check=self.check, **m))

        self.assembly_stats = None
        if 'AssemblyStats' in self.d:
            self.assembly_stats = AssemblyStats(self.mgid,
                                                db=self.db, check=self.check, **self.d['AssemblyStats'])

        self.prodigal = None
        if 'Prodigal' in self.d:
            self.prodigal = Prodigal(self.mgid, db=self.db, check=self.check, **self.d['Prodigal'])

        self.jgi_metadata = None
        if 'JgiMetadata' in self.d:
            self.jgi_metadata = JgiMetadata(self.mgid, db=self.db, check=self.check,  **self.d['JgiMetadata'])

        self.minced = None
        if 'Minced' in self.d:
            self.minced = Minced(self.mgid, db=self.db, check=self.check, **self.d['Minced'])

        self.crispr_connections = None
        if 'CrisprConnections' in self.d:
            self.crispr_connections = []
            for m in self.d['CrisprConnections']:
                self.crispr_connections.append(CrisprConnection(self.mgid, db=self.db, check=self.check, **m))

        self.hmm_searches = None
        if 'HmmSearches' in self.d:
            self.hmm_searches = []
            for m in self.d['CrisprConnections']:
                self.hmm_searches.append(HmmSearch(self.mgid, db=self.db, check=self.check, **m))

        # No MgTasks are required. TODO: Except perhaps mapping?
        self.schema = {**self.schema, **{
            'Prodigal': {'type': 'dict'},
            'AssemblyStats': {'type': 'dict'},
            'Mappings': {'type': 'list'},
            'JgiMetadata': {'type': 'dict'},
            'Minced': {'type': 'dict'},
            'CrisprConnections': {'type': 'list'},
            'mgtype': {'type': 'string',
                       'allowed': ['assembly'],
                       'required': True}
            },
            's3path': {'type': 's3file', 'required': True},
            'associated': {'type': 'dict',
                           'required': True,
                           'schema': {'sequencing': {
                                'type': 'list',
                                'schema': {'type': ['mgid',
                                                    'nonestring']},
                                'required': True
                                },
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

    def link_sequencing(self, seq_mgid, xlink=True, write=True):
        '''
        xlink = whether or not you want to also link the corresponding sequencing
        to this assembly. If this were always True, would result in infinite
        loop
        TODO: Allow this to take either an mgid or an object
        '''
        from metagenomi.models.sequencing import Sequencing
        if xlink:
            linked_sequencing = Sequencing(seq_mgid, db=self.db, load=True)
            linked_sequencing.link_assembly(self.mgid, xlink=False)

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

    def get_filtered_contigs(self, raise_error=False):
        '''
        DEPRECATED
        '''
        if self.prodigal:
            ctgs = self.prodigal.pullseq_contigs
            return ctgs
        else:
            if raise_error:
                e = f'No filtered contigs, prodigal has not been run'
                raise ValueError(e)
            else:
                return None

    # def get_contigs(self, filtered=True, raise_error=False):
    #     if filtered:
    #     if self.prodigal:
    #         ctgs = self.prodigal.pullseq_contigs
    #         return ctgs
    #     else:
    #         if raise_error:
    #             e = f'No filtered contigs, prodigal has not been run'
    #             raise ValueError(e)
    #         else:
    #             return None

    def download_contigs(self, dir_to_dl=os.getcwd(), filtered=True, overwrite=True, dry_run=False):
        if filtered:
            ctgs = self.get_filtered_contigs()
        else:
            ctgs = self.s3path
        return download_file(ctgs, dir_to_dl, dry_run=dry_run, overwrite=overwrite)

    def get_associated_sequencings(self):
        if 'sequencing' in self.associated:
            return self.associated['sequencing']
        else:
            return []

    def get_prodigal_cmd(self, cutoff=1000):
        # TODO: FIX THIS
        # genes = f"{self.s3path}.genes"
        # faa = f"{self.s3path}.genes.faa"
        # minx = self.s3path.split('.')[0]+f'_min{cutoff}.fa'
        #
        # cmd = f'python submit_prodigal_job.py --input {self.s3path} '
        # cmd += f'--output {minx} --outgenes {genes} --outfaa {faa}'

        cmd = f'python submit_prodigal_job.py --mgid {self.mgid}'

        return(cmd)

    def get_minced_cmd(self, filtered_ctgs=True, overrides=None):
        '''
        '''
        # if filtered_ctgs:
        #     ctgs = self.get_filtered_contigs()
        # else:

        if self.prodigal:
            cmd = f'python submit_minced.py --mgid {self.mgid} --gff'
            return(cmd)
        else:
            e = f'No filtered contigs, prodigal has not been run'
            raise ValueError(e)

    def get_reassembly_cmd(self, out, jobdef=None):
        # print('new')
        # if len(self.associated['sequencing']) > 1:
        #     raise ValueError('Multiple sequencings. I do not know what to assemble.')
        # seqs = [i for i in self.associated['sequencing'] if 'tran' not in i and i !='None']
        # if 'tran' in aseq:
        #     print('You are trying to assembly a transcriptome you idiot')
        #     print(f'Please delete {self.mgid}')
        #     return
        cmd = f'python submit_megahit_job.py --mgid {self.mgid} --out {out}'
        if jobdef:
            cmd += f' --job-def {jobdef}'
        return cmd
