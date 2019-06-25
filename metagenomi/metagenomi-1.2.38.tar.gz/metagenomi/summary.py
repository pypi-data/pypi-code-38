import os
import datetime
import pandas as pd
import operator

# from boto3.dynamodb.conditions import Key, Attr
from metagenomi.db import (olddb, testdb, dbconn)
from metagenomi.project import MgProject
from metagenomi.tasks.taskbase import MgTask


class MgSummary():
    def __init__(self, db=dbconn):
        self.db = db
        p = MgProject(db=self.db)
        p.load()

        self.assemblies = p.assemblies
        self.samples = p.samples
        self.sequencings = p.sequencings
        self.projects = set([i.mgproject for i in (self.sequencings + self.samples + self.assemblies)])

    def count_objects(self, mgtype):
        if mgtype == 'assembly':
            items = self.assemblies
        elif mgtype == 'sample':
            items = self.samples
        elif mgtype == 'sequencing':
            items = self.sequencings

        count = {}
        for i in items:
            proj = i.mgproject
            if proj in count:
                count[proj] = count[proj] + 1
            else:
                count[proj] = 1

        return count

    # def plot_bps_over_time(self, outputname):
    #     '''
    #     https://matplotlib.org/gallery/text_labels_and_annotations/date.html
    #     https://www.earthdatascience.org/courses/earth-analytics-python/use-time-series-data-in-python/precipitation-discharge-mass-balance/
    #     '''
    #
    #     bps_by_date = {}
    #     for s in self.sequencings:
    #         d = s.created
    #         if s.sequencing_info is None:
    #             print(s.mgid)
    #         else:
    #             bps = s.sequencing_info.bases
    #             bps_by_date[d] = bps
    #
    #     df = pd.DataFrame.from_dict(bps_by_date, orient='index')
    #
    #     df['created'] = df.index
    #     df.columns = ['created', 'bases']
    #
    #     df['Date'] = pd.to_datetime(df.created)
    #     df = df.sort_values(by='Date', ascending=True)
    #
    #     fig, ax = plt.subplots()
    #     ax.plot('Date', 'base_sum', data=df)
    #
    #     plt.savefig(outputname)

    def count_contigs(self):
        count = {}
        for i in self.assemblies:
            proj = i.mgproject
            if i.assembly_stats is not None and i.assembly_stats.status != 'SUBMITTED':
                if proj in count:
                    count[proj] = count[proj] + i.assembly_stats.total_seqs
                else:
                    count[proj] = i.assembly_stats.total_seqs
            else:
                if proj in count:
                    count[proj] = count[proj] + 0
                else:
                    count[proj] = 0
        return count



    def get_biggest_contig(self):
        maxi = 0
        for i in self.assemblies:
            if i.assembly_stats is not None:
                if i.assembly_stats.status != 'SUBMITTED':
                    m = i.assembly_stats.sequence_parameters['length']
                    if isinstance(m, list):
                        m_int = [int(i) for i in m]
                        for item in m_int:
                            if item > maxi:
                                maxi = item
        return maxi



    def count_proteins(self):
        count = {}
        for i in self.assemblies:
            proj = i.mgproject
            if i.prodigal is not None:
                if proj in count:
                    count[proj] = count[proj] + i.prodigal.proteins_predicted
                else:
                    count[proj] = i.prodigal.proteins_predicted
            else:
                if proj in count:
                    count[proj] = count[proj] + 0
                else:
                    count[proj] = 0
                # print(f'Prodigal has not yet been run on project {proj}')
        return count

    def count_assembled_bps(self):
        count = {}
        failed = []
        for i in self.assemblies:
            # print(i.mgid)
            proj = i.mgproject
            if i.assembly_stats:
                if i.assembly_stats.status != 'SUBMITTED':
                    if proj in count:
                        count[proj] = count[proj] + i.assembly_stats.total_bps
                    else:
                        count[proj] = i.assembly_stats.total_bps
            else:
                print(f'No assemblystats for {i["mgid"]}')

        return count

    def count_16s(self):
        count = {'NOT RUN': 0}
        for i in self.assemblies:
            proj = i['mgproject']
            if 'R16S' in i:
                if proj in count:
                    count[proj] = count[proj] + int(i['R16S']['num_16s'])
                else:
                    count[proj] = int(i['R16S']['num_16s'])
            else:
                count['NOT RUN'] = count['NOT RUN'] + 1
                print(i['mgid'])

        return count

    def count_16s_domains(self, as_df=True):
        count = {}
        for i in self.assemblies:
            proj = i['mgproject']
            if 'R16S' in i:
                if proj in count:
                    for k, v in i['R16S']['domains'].items():
                        if k in count[proj]:
                            count[proj][k] = count[proj][k] + v
                        else:
                            count[proj][k] = v

                else:
                    count[proj] = i['R16S']['domains']

            else:
                count['NOT RUN'] = count['NOT RUN'] + 1
                print(i['mgid'])

        if as_df:
            return pd.DataFrame(count)
        else:
            return count

    def count_bps(self, as_df=True):
        # 4 million bases per G zipped file size_mb
        # 4905611824 bp in 2710 MB size file
        # UPDATED: 1.8 million base pairs per 1 MB file size

        count = {}
        failed = []
        for i in self.sequencings:
            proj = i.mgproject
            if proj != 'PASO':
                # print(proj)
                if i.sequencing_info is not None:
                    # print('Seq info here')
                    if i.sequencing_info.bases > 0:
                        # print('bases!')
                        bases = i.sequencing_info.bases
                        if proj in count:
                            count[proj] = count[proj] + bases
                        else:
                            count[proj] = bases

                    else:
                        # print('size_mb here')
                        bases = 0
                        for k, v in i.sequencing_info.size_mb.items():
                            bases += v

                        bases = bases*1800000
                        # bases = bases*4000000
                        if proj in count:
                            count[proj] = count[proj] + bases
                        else:
                            count[proj] = bases
                else:
                    failed.append(i.mgid)

        return (count, failed)

    def get_undone_downloads(self):
        undone = {}
        for s in self.sequencings:
            if 'test' in s.s3path:
                if s.mgproject in undone:
                    undone[s.mgproject] += 1
                else:
                    undone[s.mgproject] = 1

    def print_pipeline_status(self, file=None):
        status = {}
        for p in self.projects:
            status[p] = {}

        for s in self.samples + self.sequencings + self.assemblies:
            p = s.mgproject
            v_dict = status[p]

            d = vars(s)
            for k, v in d.items():
                if k not in s.not_required:
                    if isinstance(v, MgTask):
                        vname = v.whoami()
                        if vname in v_dict:
                            v_dict[vname] += 1
                        else:
                            v_dict[vname] = 1
                    elif isinstance(v, list):
                        if isinstance(v[0], MgTask):
                            vname = v[0].whoami()
                            if vname in v_dict:
                                v_dict[vname] += 1
                            else:
                                v_dict[vname] = 1

        lengths = []
        max_length = 25
        if file is not None:
            with open(file, 'w') as f:
                for k, v in status.items():
                    f.write(k+'\n')
                    for k1, v1 in v.items():
                        # +1 for the colon
                        length = len(k1) + len(str(v1)) + 1
                        space = ' ' * (max_length - length)

                        f.write(f'\t{k1}:{space}{v1}\n')
        else:
            for k, v in status.items():
                print(k)
                for k1, v1 in v.items():
                    # +1 for the colon
                    length = len(k1) + len(str(v1)) + 1
                    space = ' ' * (max_length - length)

                    print(f'\t{k1}:{space}{v1}')

        return lengths
