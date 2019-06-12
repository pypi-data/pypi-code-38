import os
from glob import glob

def threads_num(desired_t_num, max_threads_num):
    return min(desired_t_num,max_threads_num)

def mem_per_thread(mem_mb_total,desired_t_num, max_threads_num):
    return int(mem_mb_total/threads_num(desired_t_num, max_threads_num))

def threads_num(desired_t_num, max_threads_num):
    return min(desired_t_num,max_threads_num)

def mem_per_thread(mem_mb_total,desired_t_num, max_threads_num):
    return int(mem_mb_total/threads_num(desired_t_num, max_threads_num))

def get_or_create_run_id(root_out_dir, config):
    if 'run_id' in config:
        run_id = '_' + config['run_id']
    else:
        run_id = ''
        run_num = 1
        while os.path.isfile(os.path.join(root_out_dir, 'Done_' + run_id + '.txt')):
            run_num += 1
            run_id = '_' + str(run_num)
    return run_id


def get_treat_vs_control(phenodata_file):
    treatments_list = []
    controls_list = []
    groups = {}
    combine_samples_db = {}
    with open(phenodata_file, 'r') as f:
        for l in f.readlines():
            if l.startswith('#'):
                continue
            sl = l.rstrip().split()
            if not sl:  # empty line
                continue
            else:
                group_num, sample_name, treat_or_cont = sl
                if group_num not in groups:
                    groups[group_num] = [[], []]
                if treat_or_cont == 'treatment':
                    groups[group_num][0].append(sample_name)
                else:
                    groups[group_num][1].append(sample_name)
    # Combine the required samples
    for group_num, (treatments, controls) in groups.items():
        treatments_list += combine_names(combine_samples_db, treatments)
        controls_list += combine_names(combine_samples_db, controls)
    # COMBINE_SAMPLES_DB is dictionary. key is combined name of the sampls, value is list of the combined samples. For example: {"samp1+samp2":[samp1, samp2]}
    return (combine_samples_db, treatments_list, controls_list)

def combine_names(combine, samples):
    if len(samples) > 1:
        combined_samples = '+'.join(samples)
        combine[combined_samples] = samples
        return [combined_samples]
    else:
        return samples

def get_samples(fastq_dir):
    samples = []
    combine_input_files = False
    for sample_path in glob(os.path.join(fastq_dir, '*')):
        if os.path.isfile(sample_path):
            continue
        sample_name = os.path.basename(sample_path)
        if sample_name == 'Undetermined' or sample_name == 'FastQCinput' or sample_name == 'Reports' or sample_name == 'Stats':
            continue
        if sample_name.startswith('.'):
            continue
        splitted_files_r1 = glob(os.path.join(sample_path, '*_R1_0*.fastq')) + glob(
            os.path.join(sample_path, '*_R1_0*.fastq.gz'))
        splitted_files_r2 = glob(os.path.join(sample_path, '*_R2_0*.fastq')) + glob(
            os.path.join(sample_path, '*_R2_0*.fastq.gz'))
        if len(splitted_files_r1) > 1 or len(splitted_files_r2) > 1:
            combine_input_files = True
            samples.append(sample_name)
        elif glob(os.path.join(sample_path, '*_R1*.fastq')) + glob(
                os.path.join(sample_path, '*_R1*.fastq.gz')) + glob(
            os.path.join(sample_path, '*_R2*.fastq')) + glob(
            os.path.join(sample_path, '*_R2*.fastq.gz')):
            samples.append(sample_name)
        else:
            raise IOError('Missing input file in foler %s' % sample_path)
    if not len(samples):
        raise IOError('No input fastq files in %s' % fastq_dir)
    return (samples, combine_input_files)


def concatenation_fastq(fastq_dir, fastq_dir_concat, samples):
    chunksize = 100 * 1024 * 1024  # 100 megabytes
    os.makedirs(fastq_dir_concat)
    for read in ['_R1', '_R2']:
        for sample_name in samples:
            sample_dir = os.path.join(fastq_dir, sample_name)
            sample_dir_concat = os.path.join(fastq_dir_concat, sample_name)
            os.makedirs(sample_dir_concat, exist_ok=True)
            files = sorted(glob(os.path.join(sample_dir, '*' + read + '*')))
            if files:  # Open output file only if input files of the read are exists
                if files[0][-3:] == '.gz':  # All input files are gzipped or all of them uncompressed
                    outfile = os.path.join(sample_dir_concat, sample_name + read + '.fastq.gz')
                else:
                    outfile = os.path.join(sample_dir_concat, sample_name + read + '.fastq')
                with open(outfile, 'wb') as fho:
                    for file in files:
                        with open(file, "rb") as fhi:
                            while True:
                                chunk = fhi.read(chunksize)
                                if chunk:
                                    fho.write(chunk)
                                else:
                                    break


def concatenate_fastq_files(root_out_dir, fastq_dir, samples):
    fastq_dir_concat = os.path.join(root_out_dir, '0_concatenating_fastq')
    if not os.path.isdir(fastq_dir_concat):
        concatenation_fastq(fastq_dir, fastq_dir_concat, samples)
    return fastq_dir_concat


def is_paired_end(fastq_dir_analysis, samples):
    return True if glob(os.path.join(fastq_dir_analysis, samples[0], '*_R2*')) else False


def cutadapt_template(root_out_dir, paired_end):
    return os.path.join(root_out_dir, '1_cutadapt', '{sample}_R1.fastq,') + \
           os.path.join(root_out_dir, '1_cutadapt', '{sample}_R2.fastq') if paired_end else os.path.join(root_out_dir,
                                                                                                         '1_cutadapt',
                                                                                                         '{sample}_R1.fastq')
