# To migrate the data from the defunct database
import os
import datetime

from boto3.dynamodb.conditions import Key, Attr
from metagenomi.db import (olddb, testdb, dbconn)
from metagenomi.helpers import (to_int, to_decimal, to_latlon)
from metagenomi.helpers import in_db
from metagenomi.tasks.mapping import Mapping
from metagenomi.tasks.assemblystats import AssemblyStats
from metagenomi.tasks.sampleinfo import SampleInfo
from metagenomi.tasks.prodigal import Prodigal
from metagenomi.tasks.nonpareil import Nonpareil
from metagenomi.tasks.cleaning import (QualityTrimming, AdapterRemoval, ContaminantRemoval)
from metagenomi.tasks.sequencinginfo import SequencingInfo

from metagenomi.models.assembly import Assembly
from metagenomi.models.sample import Sample
from metagenomi.models.sequencing import Sequencing

from metagenomi.helpers import download_file

import pandas as pd
import numpy as np


def get_sequence_parameters(sp):
    '''
    Return pandas dataframe of top 10 sequences and their parameters
    '''

    df = pd.DataFrame(sp)
    df['length'] = pd.to_numeric(df["length"])
    df['gc'] = pd.to_numeric(df["G+C"])
    df['non_ns'] = pd.to_numeric(df["Non-Ns"])
    df['sequence'] = df.index

    df = df.drop(columns=['G+C', 'Non-Ns'])

    return df.reset_index(drop=True)


def get_longest_contig(sp):
    df = get_sequence_parameters(sp)
    name = df['length'].idxmax()
    value = df['length'][name]
    return (name, value)


def get_end(s, sp):
    ls = s.split('-')
    # Last item in range
    if ls[1] == '':
        return get_longest_contig(sp)[1]
    else:
        return(int(ls[1]))


def get_length_distribution(ld, sp, as_df=True):
    '''
    Return pandas dataframe of length distributions
    '''

    if as_df:
        df = pd.DataFrame(ld)
        df['start'] = [int(i.split('-')[0]) for i in df['range']]
        df['end'] = [get_end(i, sp) for i in df['range']]

        cols = df.columns
        df[cols] = df[cols].apply(pd.to_numeric, errors='coerce')

        df = df.drop(columns=['range'])
        return df


def fix_prey_assembly(a, db=dbconn):
    newd = {}
    newd['s3path'] = a['s3-path']
    newd['mgid'] = a['mg-identifier']
    newd['associated'] = {'sequencing': a['associated']['read']}

    assembly = Assembly(**newd, db=db)

    # Extras: Mappings
    if 'mapping' in a:
        newmappings = []
        for i in a['mapping']:
            newtask = {}
            newtask['cmd_run'] = i['cmd_run']
            newtask['jobid'] = 'None'

            newtask['aligned_mapq_greaterequal_10'] = to_int(i['aligned_mapq_greaterequal_10'])
            newtask['aligned_mapq_less_10'] = to_int(i['aligned_mapq_less_10'])
            newtask['percent_pairs'] = to_decimal(i['percent_pairs'])
            newtask['reads_per_sec'] = to_int(i['reads_per_sec'])
            newtask['seed_size'] = to_int(i['seed_size'])
            newtask['time_in_aligner_seconds'] = to_int(i['time_in_aligner_seconds'])
            newtask['too_short_or_too_many_nns'] = to_int(i['too_short_OR_too_many_NNs'])
            newtask['total_bases'] = to_int(i['total_bases'])
            newtask['total_reads'] = to_int(i['total_reads'])
            newtask['unaligned'] = to_int(i['unaligned'])
            newtask['reads_mapped'] = {'fwd': i['reads_mapped'][0],
                                       'rev': i['reads_mapped'][1]}
            newtask['reference'] = i['ref']

            newmappings.append(Mapping(assembly.mgid, **newtask))

        assembly.mappings = newmappings

    # AssemblyStats
    if 'megahit_metadata' in a:
        i = a['megahit_metadata']
        newtask = {}
        newtask['cmd_run'] = i['cmds_run']
        newtask['jobid'] = 'None'
        newtask['total_seqs'] = i['total_seqs']
        newtask['total_bps'] = i['total_bps']
        newtask['n50'] = i['n50']
        newtask['avg_sequence_len'] = i['avg_seq_len']
        newtask['assembler'] = 'megahit'

        sp = i['Sequence parameters']
        ld = i['Length distribution']

        newtask['sequence_parameters'] = get_sequence_parameters(sp).replace([np.nan, ''],
                                                   'None')
        newtask['length_distribution'] = get_length_distribution(ld, sp).replace([np.nan, ''],
                                                   'None')

        assembly.assembly_stats = AssemblyStats(assembly.mgid, **newtask)

    # Try to predict the prodigal stuff
    faa = f'{assembly.s3path}.genes.faa'
    ctgs = assembly.s3path.split('_min1000')[0]+'.fa'

    localfaa = download_file(faa, os.getcwd())
    localctgs = download_file(ctgs, os.getcwd())
    localpullseqctgs = download_file(assembly.s3path, os.getcwd())

    proteins_predicted = len([1 for line in open(localfaa) if line.startswith(">")])
    contigs_above_cutoff = len([1 for line in open(localpullseqctgs) if line.startswith(">")])
    all_contigs = len([1 for line in open(localctgs) if line.startswith(">")])

    os.remove(localfaa)
    os.remove(localctgs)
    os.remove(localpullseqctgs)

    newtask = {}
    newtask['cmd_run'] = 'None'
    newtask['jobid'] = 'None'
    newtask['mode'] = 'meta'
    newtask['pullseq_contigs'] = assembly.s3path
    newtask['protein_file'] = faa
    newtask['min_sequence_length'] = 1000
    newtask['proteins_predicted'] = proteins_predicted
    newtask['contigs_above_cutoff'] = contigs_above_cutoff
    newtask['contigs_below_cutoff'] = all_contigs - contigs_above_cutoff

    assembly.s3path = ctgs
    assembly.prodigal = Prodigal(assembly.mgid, **newtask)
    return assembly


def fix_prey_sample(s, db=testdb):
    newd = {}
    newd['mgid'] = s['mg-identifier']
    newd['associated'] = {'sequencing': s['associated']['read']}
    # s.pop('associated')
    sample = Sample(**newd, db=db)

    if 'metadata' in s:
        i = s['metadata']
        newtask = {}
        newtask['cmd_run'] = 'None'
        newtask['jobid'] = 'None'
        newtask['collection_date'] = i.pop('collection date')
        newtask['depth_cm'] = i.pop('depth (cm)')
        newtask['description'] = i.pop('description')
        newtask['geographic_location'] = i.pop('geographic location')
        newtask['isolation_source'] = i.pop('isolation source')
        newtask['latlon'] = i.pop('latitude and longitude')
        newtask['ph'] = i.pop('pH')
        if i['plant associated'] == 'nan':
            newtask['plant_associated'] = 'None'
        elif 'Yes' in i['plant associated'] or 'true' in i['plant associated'] or 'True' in i['plant associated']:
            newtask['plant_associated'] = True
        else:
            newtask['plant_associated'] = False
        i.pop('plant associated')

        newtask['sample_color'] = i.pop('sample color')
        newtask['sample_id'] = i.pop('sample_id')

        i.pop('mg_identifier')

        newtask['extra_metadata'] = i

        si = SampleInfo(sample.mgid, db=db, **newtask)

        sample.sample_info = si
        print(sample.db.table)

        sample.write()


def fix_prey_sequencing(s, db=dbconn):
    newd = {}
    newd['mgid'] = s['mg-identifier']
    assocsamples = ['None']
    assocassemblies = ['None']
    if 'sample' in s['associated']:
        assocsamples = s['associated']['sample']
    if 'assembly' in s['associated']:
        assocassemblies = s['associated']['assembly']

    newd['associated'] = {'sample': assocsamples, 'assembly': assocassemblies}
    newd['s3path'] = s['s3-path']

    # print(newd)

    seq = Sequencing(**newd, db=db)
    # seq.write()

    if 'nonpareil_metadata' in s:
        i = s['nonpareil_metadata']
        # for k,v in i.items():
        #     print(k)
        newtask = {}
        newtask['cmd_run'] = 'None'
        if 'cmd' in i:
            newtask['cmd_run'] = i['cmd']

        newtask['jobid'] = 'None'

        newtask['diversity'] = to_decimal(i['diversity'])

        if 'input' in i:
            newtask['input'] = i['input']
        elif 'run_on' in i:
            newtask['input'] = i['run_on']
        else:
            newtask['input'] = 'None'

        newtask['kappa'] = to_decimal(i['kappa'])
        newtask['lr'] = to_decimal(i['LR'])
        newtask['lr_star'] = to_decimal(i['LRstar'])
        newtask['modelr'] = to_decimal(i['modelR'])

        output = f's3://metagenomi/projects/rey/reads/qc/nonpareil/{seq.mgid}_trim_clean_nonpareil'
        pdf = f's3://metagenomi/projects/rey/reads/qc/nonpareil/{seq.mgid}_trim_clean_nonpareil.pdf'
        tsv = f's3://metagenomi/projects/rey/reads/qc/nonpareil/{seq.mgid}_trim_clean_nonpareil.tsv'
        newtask['output'] = output
        newtask['pdf'] = pdf
        newtask['tsv'] = tsv
        newtask['c'] = to_decimal(i['C'])

        nonp = Nonpareil(seq.mgid, db=db, **newtask)
        seq.nonpareil = nonp

    if 'bbmap_metadata' in s:
        ss = s['bbmap_metadata']

        if 'adapter_removal' in ss:
            i = ss['adapter_removal']
            newtask = {}
            newtask['cmd_run'] = i['cmd_run']
            newtask['jobid'] = 'None'
            newtask['ftrimmed_reads'] = to_int(i['FTrimmed_reads'])
            newtask['ktrimmed_reads'] = to_int(i['KTrimmed_reads'])
            newtask['total_removed_reads'] = to_int(i['total_removed_reads'])
            newtask['trimmed_by_overlap_reads'] = to_int(i['trimmed_by_overlap_reads'])
            newtask['output'] = {'fwd': s['s3-path']+'.1.fastq.gz', 'rev': s['s3-path']+'.2.fastq.gz'}
            # print(newtask)

            ar = AdapterRemoval(seq.mgid, db=db, **newtask)
            seq.adapter_removal = ar
            total_bases = i['total_bases']
            total_reads = i['total_reads']

        if 'contaminant_removal' in ss:
            i = ss['contaminant_removal']
            newtask = {}
            newtask['cmd_run'] = i['cmd_run']
            newtask['jobid'] = 'None'

            newtask['total_removed_reads'] = i['total_removed_reads']
            newtask['output'] = {'fwd': s['s3-path']+'.1.fastq.gz', 'rev': s['s3-path']+'.2.fastq.gz'}

            cr = ContaminantRemoval(seq.mgid, db=db, **newtask)
            seq.contaminant_removal = cr

        if 'quality_trimming' in ss:
            i = ss['quality_trimming']
            newtask = {}
            newtask['cmd_run'] = i['cmd_run']
            newtask['jobid'] = 'None'
            newtask['total_removed_reads'] = i['total_removed_reads']
            newtask['output'] = {'fwd': s['s3-path']+'.1.fastq.gz', 'rev': s['s3-path']+'.2.fastq.gz'}

            qt = QualityTrimming(seq.mgid, db=db, **newtask)
            seq.quality_trimming = qt

    if 'metadata' in s:
        i = s['metadata']
        newtask = {}
        newtask['cmd_run'] = 'None'
        newtask['jobid'] = 'None'
        newtask['avg_length'] = to_decimal(i.pop('avgLength'))
        newtask['bases'] = to_int(i.pop('bases'))
        newtask['insert_size'] = to_int(i.pop('InsertSize'))
        newtask['library_layout'] = i.pop('LibraryLayout')
        newtask['library_selection'] = i.pop('LibrarySelection')
        newtask['library_source'] = i.pop('LibrarySource')
        newtask['library_strategy'] = i.pop('LibraryStrategy')
        newtask['model'] = i.pop('Model')
        newtask['platform'] = i.pop('Platform')

        rpaths = i.pop('raw_reads')
        newtask['raw_read_paths'] = {'fwd': rpaths[0],
                                     'rev': rpaths[1]}
        newtask['sample_name'] = i.pop('SampleName')

        smb = list(i.pop('size_MB').keys())
        newtask['size_mb'] = {'fwd': smb[0],
                              'rev': smb[1]}
        newtask['spots'] = i.pop('spots')
        newtask['spots_with_mates'] = i.pop('spots_with_mates')
        newtask['reads'] = total_reads

        print(newtask)

        seqinfo = SequencingInfo(seq.mgid, db=db, **newtask)
        seq.sequencing_info = seqinfo

    return(seq)


def fix_htsp_sequencing(s, db=testdb):
    newd = {}
    newd['mgid'] = s['mg-identifier']
    assocsamples = ['None']
    assocassemblies = ['None']
    if 'sample' in s['associated']:
        assocsamples = s['associated']['sample']
    if 'assembly' in s['associated']:
        assocassemblies = s['associated']['assembly']

    newd['associated'] = {'sample': assocsamples, 'assembly': assocassemblies}
    newd['s3path'] = s['s3-path']

    seq = Sequencing(**newd, db=db)

    if 'nonpareil_metadata' in s:
        i = s['nonpareil_metadata']
        # for k,v in i.items():
        #     print(k)
        newtask = {}
        newtask['cmd_run'] = 'None'
        if 'cmd' in i:
            newtask['cmd_run'] = i['cmd']

        newtask['jobid'] = 'None'

        newtask['diversity'] = to_decimal(i['diversity'])

        if 'input' in i:
            newtask['input'] = i['input']
        elif 'run_on' in i:
            newtask['input'] = i['run_on']
        else:
            newtask['input'] = 'None'

        newtask['kappa'] = to_decimal(i['kappa'])
        newtask['lr'] = to_decimal(i['LR'])
        newtask['lr_star'] = to_decimal(i['LRstar'])
        newtask['modelr'] = to_decimal(i['modelR'])

        newtask['output'] = i['output']
        newtask['pdf'] = i['pdf']
        newtask['tsv'] = i['tsv']
        newtask['c'] = to_decimal(i['C'])

        nonp = Nonpareil(seq.mgid, db=db, **newtask)
        seq.nonpareil = nonp

    if 'bbmap_metadata' in s:
        ss = s['bbmap_metadata']

        if 'adapter_removal' in ss:
            i = ss['adapter_removal']
            newtask = {}
            newtask['cmd_run'] = i['cmd_run']
            newtask['jobid'] = 'None'
            newtask['ftrimmed_reads'] = to_int(i['FTrimmed_reads'])
            newtask['ktrimmed_reads'] = to_int(i['KTrimmed_reads'])
            newtask['total_removed_reads'] = to_int(i['total_removed_reads'])
            newtask['trimmed_by_overlap_reads'] = to_int(i['trimmed_by_overlap_reads'])
            newtask['output'] = {'fwd': s['s3-path']+'.1.fastq.gz', 'rev': s['s3-path']+'.2.fastq.gz'}
            # print(newtask)

            ar = AdapterRemoval(seq.mgid, db=db, **newtask)
            seq.adapter_removal = ar
            total_bases = i['total_bases']
            total_reads = i['total_reads']

        if 'contaminant_removal' in ss:
            i = ss['contaminant_removal']
            newtask = {}
            newtask['cmd_run'] = i['cmd_run']
            newtask['jobid'] = 'None'

            newtask['total_removed_reads'] = i['total_removed_reads']
            newtask['output'] = {'fwd': s['s3-path']+'.1.fastq.gz', 'rev': s['s3-path']+'.2.fastq.gz'}

            cr = ContaminantRemoval(seq.mgid, db=db, **newtask)
            seq.contaminant_removal = cr

        if 'quality_trimming' in ss:
            i = ss['quality_trimming']
            newtask = {}
            newtask['cmd_run'] = i['cmd_run']
            newtask['jobid'] = 'None'
            newtask['total_removed_reads'] = i['total_removed_reads']
            newtask['output'] = {'fwd': s['s3-path']+'.1.fastq.gz', 'rev': s['s3-path']+'.2.fastq.gz'}

            qt = QualityTrimming(seq.mgid, db=db, **newtask)
            seq.quality_trimming = qt

    if 'metadata' in s:
        i = s['metadata']
        newtask = {}
        newtask['cmd_run'] = 'None'
        newtask['jobid'] = 'None'
        newtask['avg_length'] = to_decimal(i.pop('avgLength'))
        newtask['bases'] = to_int(i.pop('bases'))
        newtask['insert_size'] = to_int(i.pop('InsertSize'))
        newtask['library_layout'] = i.pop('LibraryLayout')
        newtask['library_selection'] = i.pop('LibrarySelection')
        newtask['library_source'] = i.pop('LibrarySource')
        newtask['library_strategy'] = i.pop('LibraryStrategy')
        newtask['model'] = i.pop('Model')
        newtask['platform'] = i.pop('Platform')

        newtask['raw_read_paths'] = {'fwd': 'None',
                                     'rev': 'None'}
        newtask['sample_name'] = str(i.pop('SampleName'))
        bothsize = to_decimal(i.pop('size_MB'))
        newtask['size_mb'] = {'fwd': bothsize/2, 'rev': bothsize/2}

        newtask['spots'] = i.pop('spots')
        newtask['spots_with_mates'] = i.pop('spots_with_mates')
        newtask['reads'] = newtask['spots']
        newtask['extra_metadata'] = i

        seqinfo = SequencingInfo(seq.mgid, db=db, **newtask)
        seq.sequencing_info = seqinfo

    return(seq)


def fix_htsp_sample(s, db=dbconn):
    newd = {}
    newd['mgid'] = s['mg-identifier']
    newd['associated'] = {'sequencing': s['associated']['read']}
    # s.pop('associated')
    sample = Sample(**newd, db=db, check=False)

    if 'metadata' in s:
        i = s['metadata']
        newtask = {}
        newtask['cmd_run'] = 'None'
        newtask['jobid'] = 'None'
        newtask['collection_date'] = i.pop('collection date')

        newtask['depth_cm'] = 'None'
        if 'description' in i:
            newtask['description'] = i.pop('description')
        else:
            newtask['description'] = 'None'

        newtask['geographic_location'] = i.pop('geographic location')
        newtask['isolation_source'] = i.pop('isolation source')

        country = None
        if ':' in newtask['geographic_location']:
            country = newtask['geographic_location'].split(':')[0]

        if 'geographic location (longitude)' in i and 'geographic location (latitude)' in i:
            lat = i['geographic location (latitude)'].split(' ')[0]
            lon = i['geographic location (longitude)'].split(' ')[0]
            newtask['latlon'] = to_latlon(f'{lat}, {lon}', country)

        else:
            newtask['latlon'] = to_latlon(i.pop('latitude and longitude'), country)

        newtask['ph'] = 'None'
        if 'plant_associated' in i:
            if i['plant associated'] == 'nan':
                newtask['plant_associated'] = 'None'
            elif 'Yes' in i['plant associated'] or 'true' in i['plant associated'] or 'True' in i['plant associated']:
                newtask['plant_associated'] = True
            else:
                newtask['plant_associated'] = False
            i.pop('plant associated')
        else:
            newtask['plant_associated'] = 'None'

        if 'sample_color' in i:
            newtask['sample_color'] = i.pop('sample color')
        else:
            newtask['sample_color'] = 'None'

        if 'sample_id' in i:
            newtask['sample_id'] = i.pop('sample_id')
        else:
            newtask['sample_id'] = 'None'

        if 'mg_identifier' in i:
            i.pop('mg_identifier')

        newtask['extra_metadata'] = i

        print(newtask)

        si = SampleInfo(sample.mgid, check=False, db=db, **newtask)
        print(si.to_dict(validate=False))
        print('Collection date = ', si.collection_date)

        sample.sample_info = si

    return sample
        # print(sample.db.table)

        # sample.write()


def fix_htsp_assm(s, db=dbconn):
    newd = {}
    newd['mgid'] = s['mg-identifier']
    newd['associated'] = {'sequencing': s['associated']['read']}
    newd['s3path'] = s['s3-path']
    # s.pop('associated')
    assm = Assembly(**newd, db=db, check=False)

    if 'megahit_metadata' in s:
        i = s['megahit_metadata']
        newtask = {}
        newtask['cmd_run'] = i.get('cmds_run', 'None')
        newtask['jobid'] = 'None'
        newtask['total_seqs'] = int(i['total_seqs'])
        newtask['total_bps'] = int(i['total_bps'])
        newtask['n50'] = int(i['n50'])
        newtask['avg_sequence_len'] = i['avg_seq_len']
        newtask['assembler'] = 'megahit'

        sp = i['Sequence parameters']
        ld = i['Length distribution']

        newtask['sequence_parameters'] = get_sequence_parameters(sp).replace([np.nan, ''],
                                                   'None')
        newtask['length_distribution'] = get_length_distribution(ld, sp).replace([np.nan, ''],
                                                   'None')

        # print(newtask)
        assm.assembly_stats = AssemblyStats(assm.mgid, **newtask)


    # Prodigal
    # Try to predict the prodigal stuff

    faa = f'{assm.s3path}.genes.faa'
    ctgs = assm.s3path.split('_min1000')[0]+'.fa'

    localfaa = download_file(faa, os.getcwd())
    localctgs = download_file(ctgs, os.getcwd())
    localpullseqctgs = download_file(assm.s3path, os.getcwd())

    proteins_predicted = len([1 for line in open(localfaa) if line.startswith(">")])
    contigs_above_cutoff = len([1 for line in open(localpullseqctgs) if line.startswith(">")])
    all_contigs = len([1 for line in open(localctgs) if line.startswith(">")])

    os.remove(localfaa)
    os.remove(localctgs)
    os.remove(localpullseqctgs)

    newtask = {}
    newtask['cmd_run'] = 'None'
    newtask['jobid'] = 'None'
    newtask['mode'] = 'meta'
    newtask['pullseq_contigs'] = assm.s3path
    newtask['protein_file'] = faa
    newtask['min_sequence_length'] = 1000
    newtask['proteins_predicted'] = proteins_predicted
    newtask['contigs_above_cutoff'] = contigs_above_cutoff
    newtask['contigs_below_cutoff'] = all_contigs - contigs_above_cutoff

    assm.s3path = ctgs
    assm.prodigal = Prodigal(assm.mgid, **newtask)

    return assm


def main(project='PREY', db=dbconn):
    preyitems = scan(olddb, filter_key='mg-identifier', filter_value=project)
    # htspitems = scan(olddb, filter_key='mg-identifier', filter_value='HTSP')

    for i in preyitems:
        # if 'assm' in i['mg-identifier']:
        #     if not in_db(i['mg-identifier'], db):
        #         print(i['mg-identifier'])
        #         newd = fix_prey_assembly(i, db=db)
        #         print('writing to : ', newd.db.table)
        #         newd.write(force=False, ignore_exceptions=True)
        #
        #     else:
        #         mgid = i['mg-identifier']
        #         print(f'{mgid} already in the database')

        # if 'samp' in i['mg-identifier']:
        #     if not in_db(i['mg-identifier'], db):
        #         print(i['mg-identifier'])
        #         fix_prey_sample(i, db=db)
        #     else:
        #         mgid = i['mg-identifier']
        #         print(f'{mgid} already in the database')

        if 'tran' in i['mg-identifier']:
            print(i['mg-identifier'])
            s = fix_prey_sequencing(i, db=db)
            # s.write(force=True)
            print(s.created)
            # print(s.to_dict(validate=True, clean=True))
            print(s.db.table)
            s.write(force=False)


        # if '-samp' in i['mg-identifier']:
        #     print(i['mg-identifier'])
        #     s = fix_htsp_sample(i, db=db)
        #     s.write()
        #     print(s.created)

        # if '-assm' in i['mg-identifier']:
        #     print(i['mg-identifier'])
        #     s = fix_htsp_assm(i, db=db)
        #     print(s.created)
        #     s.write()

        # HOTSPRINGS





            # print(newd.db.table)


    # Step 1: pull everything from the old database in
    # project wise or object wise?
    # Should I do this in python???

    # Check if it

    # Step 2: for each project, munge the data

    # Step 3: Try to validate, check errors

    # Step 4:

def scan(db, filter_key=None, filter_value=None, comparison='contains'):
    """
    not currently in use
    """

    if filter_key and filter_value:
        if comparison == 'equals':
            filtering_exp = Key(filter_key).eq(filter_value)
        elif comparison == 'contains':
            filtering_exp = Attr(filter_key).contains(filter_value)

        response = db.table.scan(
            FilterExpression=filtering_exp)

    else:
        response = db.table.scan()

    items = response['Items']
    while True:
        if response.get('LastEvaluatedKey'):
            response = db.table.scan(
                ExclusiveStartKey=response['LastEvaluatedKey'],
                FilterExpression=filtering_exp
                )
            items += response['Items']
        else:
            break

    return items


if __name__ == '__main__':
    main()
