from Benchmark.byteformat import B2GB, B2MB, MB2GB, GB2MB
from Benchmark.classes import BenchmarkResult


def mergebed(input_json):
    assert 'input_size_in_bytes' in input_json
    insz = input_json['input_size_in_bytes']
    assert 'input_bed' in insz
    input_size = sum(insz['input_bed'])
    total_size_in_gb = B2GB((input_size * 5) * 3)
    r = BenchmarkResult(size=total_size_in_gb,
                        mem=1024,
                        cpu=2)
    return(r.as_dict())


def encode_atacseq_aln(input_json):
    assert 'input_size_in_bytes' in input_json
    insz = input_json['input_size_in_bytes']
    assert 'atac.fastqs' in insz
    assert 'atac.bowtie2_idx_tar' in insz
    input_fastq_size = sum(insz['atac.fastqs'])
    if input_json['parameters'].get('atac.paired_end', ''):
        nTechRep = len(insz['atac.fastqs']) / 2 # we assume one biological replicate
    else:
        nTechRep = len(insz['atac.fastqs'])
    print("nTechRep = " + str(nTechRep))
    total_size_in_gb = B2GB((input_fastq_size * 5 + insz['atac.bowtie2_idx_tar'] * 2.5) * nTechRep) * 1.5
    if 'parameters' in input_json and 'atac.bowtie2.cpu' in input_json['parameters']:
        cpu = input_json['parameters']['atac.bowtie2.cpu']
    else:
        cpu = 2
    mem = 6 + 2 * (nTechRep - 1)
    r = BenchmarkResult(size=total_size_in_gb,
                        mem=GB2MB(mem),
                        cpu=cpu,
                        exclude_t=True)
    return(r.as_dict())


def encode_atacseq_postaln(input_json):
    assert 'input_size_in_bytes' in input_json
    insz = input_json['input_size_in_bytes']
    assert 'atac.tas' in insz
    input_size = sum(insz['atac.tas'])
    nRep = len(insz['atac.tas'])
    total_size_in_gb = (B2GB(input_size * 55) + 16 * (nRep - 1)) * 2.5
    cpu = 12 + 4 * (nRep - 1)
    mem = 8 + 4 * (nRep - 1)
    r = BenchmarkResult(size=total_size_in_gb,
                        mem=GB2MB(mem),
                        cpu=cpu,
                        exclude_t=True)
    return(r.as_dict())


def encode_chipseq_aln_chip(input_json):
    assert 'input_size_in_bytes' in input_json
    insz = input_json['input_size_in_bytes']
    assert 'chip.fastqs' in insz
    assert 'chip.bwa_idx_tar' in insz
    input_fastq_size = sum(insz['chip.fastqs'])
    total_size_in_gb = B2GB(input_fastq_size * 6 + insz['chip.bwa_idx_tar'] * 4) * 1.2
    if 'parameters' in input_json and 'chip.bwa.cpu' in input_json['parameters']:
        cpu = input_json['parameters']['chip.bwa.cpu']
    else:
        cpu = 2
    r = BenchmarkResult(size=total_size_in_gb,
                        mem=GB2MB(16),
                        cpu=cpu if cpu >= 8 else 8,
                        exclude_t=True)
    return(r.as_dict())


def encode_chipseq_aln_ctl(input_json):
    assert 'input_size_in_bytes' in input_json
    insz = input_json['input_size_in_bytes']
    assert 'chip.ctl_fastqs' in insz
    assert 'chip.bwa_idx_tar' in insz
    input_fastq_size = sum(insz['chip.ctl_fastqs'])
    total_size_in_gb = B2GB(input_fastq_size * 6 + insz['chip.bwa_idx_tar'] * 4) * 1.2
    if 'parameters' in input_json and 'chip.bwa_ctl.cpu' in input_json['parameters']:
        cpu = input_json['parameters']['chip.bwa_ctl.cpu']
    else:
        cpu = 2
    r = BenchmarkResult(size=total_size_in_gb,
                        mem=GB2MB(10),
                        cpu=cpu if cpu >= 8 else 8,
                        exclude_t=True)
    return(r.as_dict())


def encode_chipseq_postaln(input_json):
    assert 'input_size_in_bytes' in input_json
    insz = input_json['input_size_in_bytes']
    assert 'chip.tas' in insz
    assert 'chip.bam2ta_no_filt_R1.ta' in insz
    input_size = sum(insz['chip.tas']) + sum(insz.get('chip.ctl_tas', [0])) \
                 + sum(insz['chip.bam2ta_no_filt_R1.ta'])
    total_size_in_gb = B2GB(input_size * 35) * 3
    if 'parameters' in input_json and 'chip.spp_cpu' in input_json['parameters']:
        cpu = input_json['parameters']['chip.spp_cpu']
    else:
        cpu = 2
    r = BenchmarkResult(size=total_size_in_gb,
                        mem=GB2MB(cpu * 7),
                        cpu=cpu * 4,
                        exclude_t=True)
    return(r.as_dict())


def encode_chipseq(input_json):
    assert 'input_size_in_bytes' in input_json
    insz = input_json['input_size_in_bytes']
    assert 'chip.fastqs' in insz
    assert 'chip.bwa_idx_tar' in insz
    input_fastq_size = sum(insz['chip.fastqs']) + sum(insz.get('chip.ctl_fastqs', [0]))
    input_size = input_fastq_size + insz['chip.bwa_idx_tar']
    output_size = input_fastq_size * 8 + insz['chip.bwa_idx_tar'] * 4
    total_size_in_gb = B2GB(input_size + output_size)
    r = BenchmarkResult(size=total_size_in_gb,
                        mem=30000,
                        cpu=16)
    return(r.as_dict())


def encode_atacseq(input_json):
    assert 'input_size_in_bytes' in input_json
    insz = input_json['input_size_in_bytes']
    assert 'atac.fastqs' in insz
    assert 'atac.bowtie2_idx_tar' in insz
    input_fastq_size = sum(insz['atac.fastqs'])
    input_size = input_fastq_size + insz['atac.bowtie2_idx_tar']
    output_size = input_fastq_size * 10
    total_size_in_gb = B2GB(input_size + output_size)
    if 'parameters' in input_json and  'atac.bowtie2.cpu' in input_json['parameters']:
        cpu = input_json['parameters']['atac.bowtie2.cpu'] + 2
    else:
        cpu = 6
    r = BenchmarkResult(size=total_size_in_gb,
                        mem=16000,
                        cpu=cpu)
    return(r.as_dict())



def md5(input_json):
    assert 'input_size_in_bytes' in input_json
    assert 'input_file' in input_json.get('input_size_in_bytes')
    input_in_bytes = input_json.get('input_size_in_bytes').get('input_file')
    input_size = B2GB(input_in_bytes) + 3
    r = BenchmarkResult(size=input_size,
                        mem=1024,
                        cpu=1)

    return(r.as_dict())


def fastqc_0_11_4_1(input_json):
    assert 'input_size_in_bytes' in input_json
    assert 'input_fastq' in input_json.get('input_size_in_bytes')

    nthreads = 1  # default value according to the cwl
    if 'parameters' in input_json:
        if 'threads' in input_json.get('parameters'):
            nthreads = input_json.get('parameters').get('threads')

    input_in_bytes = input_json.get('input_size_in_bytes').get('input_fastq')
    input_size = B2GB(input_in_bytes) * 2 + 3
    if input_size > 100:
        input_size = input_size + 20
    mem = 300 * nthreads
    if mem < 1024:
        mem = 1024
    r = BenchmarkResult(size=input_size,
                        mem=mem,
                        cpu=nthreads)

    return(r.as_dict())


def bwa_mem(input_json):
    assert 'input_size_in_bytes' in input_json
    assert 'fastq1' in input_json.get('input_size_in_bytes')
    assert 'fastq2' in input_json.get('input_size_in_bytes')
    assert 'bwa_index' in input_json.get('input_size_in_bytes')

    # cpu
    nthreads = 4  # default from cwl
    if 'parameters' in input_json:
        if 'nThreads' in input_json.get('parameters'):
            nthreads = input_json.get('parameters').get('nThreads')

    # space
    input_sizes = input_json.get('input_size_in_bytes')
    data_input_size = input_sizes.get('fastq1') + input_sizes.get('fastq2')
    total_input_size = data_input_size + input_sizes.get('bwa_index')
    output_bam_size = data_input_size * 2
    intermediate_index_size = input_sizes.get('bwa_index') * 2
    copied_input_size = data_input_size * 7  # copied and unzipped
    total_intermediate_size \
        = intermediate_index_size + output_bam_size + copied_input_size
    total_output_size = output_bam_size
    additional_size_in_gb = 10

    total_file_size_in_bp \
        = total_input_size + total_intermediate_size + total_output_size
    total_size = B2GB(total_file_size_in_bp) + additional_size_in_gb

    # mem
    mem = B2MB(input_sizes.get('bwa_index') * 4) + (nthreads * 500)

    r = BenchmarkResult(size=total_size, mem=mem, cpu=nthreads)

    return(r.as_dict())


def insulator_score_caller(input_json):
    assert 'input_size_in_bytes' in input_json
    assert 'mcoolfile' in input_json.get('input_size_in_bytes')

    # cpu
    nthreads = 1

    # space
    input_sizes = input_json.get('input_size_in_bytes')
    data_input_size = input_sizes.get('mcoolfile')
    total_input_size = data_input_size
    output_bw_size = data_input_size * 0.001
    total_output_size = output_bw_size
    additional_size_in_gb = 2
    total_file_size_in_bp \
        = total_input_size + total_output_size
    total_size = B2GB(total_file_size_in_bp) + additional_size_in_gb

    # mem
    mem = GB2MB(2)

    r = BenchmarkResult(size=total_size, mem=mem, cpu=nthreads)

    return(r.as_dict())


def pairsam_parse_sort(input_json):
    assert 'input_size_in_bytes' in input_json
    assert 'bam' in input_json.get('input_size_in_bytes')

    # cpu
    nthreads = 8  # default from cwl
    if 'parameters' in input_json:
        if 'nThreads' in input_json.get('parameters'):
            nthreads = input_json.get('parameters').get('nThreads')

    in_size = input_json.get('input_size_in_bytes')
    bamsize = B2GB(in_size.get('bam'))
    pairsamsize = bamsize * 10  # very rough number
    tmp_pairsamsize = pairsamsize
    total_size = bamsize + pairsamsize + tmp_pairsamsize
    mem = 48000  # very rough number

    r = BenchmarkResult(size=total_size, mem=mem, cpu=nthreads * 2)

    return(r.as_dict())


def pairsam_merge(input_json):
    assert 'input_size_in_bytes' in input_json
    assert 'input_pairsams' in input_json.get('input_size_in_bytes')
    in_size = input_json['input_size_in_bytes']
    assert isinstance(in_size['input_pairsams'], list)

    # cpu
    nthreads = 8  # default from cwl
    if 'parameters' in input_json:
        if 'nThreads' in input_json.get('parameters'):
            nthreads = input_json.get('parameters').get('nThreads')

    # space
    input_size = B2GB(sum(in_size['input_pairsams']))
    total_size = input_size * 3
    total_safe_size = total_size * 2

    # mem
    mem = 4000

    # 32 cores: 1.8G/min (c4.8xlarge), 8 cores: 0.9G/min (r4.2xlarge)

    r = BenchmarkResult(size=total_safe_size, mem=mem, cpu=nthreads)
    return(r.as_dict())


def pairsam_markasdup(input_json):
    assert 'input_size_in_bytes' in input_json
    assert 'input_pairsam' in input_json.get('input_size_in_bytes')

    cpu = 1  # very rough estimate
    mem = 15000  # very rough estimate

    # space
    insize = B2GB(input_json['input_size_in_bytes']['input_pairsam'])
    outsize = insize
    intersize = outsize
    total_size = insize + outsize + intersize
    total_safe_size = total_size * 2

    r = BenchmarkResult(size=total_safe_size, mem=mem, cpu=cpu)
    return(r.as_dict())


def pairsam_filter(input_json):
    assert 'input_size_in_bytes' in input_json
    assert 'input_pairsam' in input_json.get('input_size_in_bytes')

    cpu = 4  # very rough estimate
    mem = 16000  # very rough estimate

    # space
    insize = B2GB(input_json['input_size_in_bytes']['input_pairsam'])
    outbamsize = insize
    outpairssize = insize  # to be safe
    outsize = outbamsize + outpairssize
    intersize = outsize
    total_size = insize + outsize + intersize
    total_safe_size = total_size * 2

    r = BenchmarkResult(size=total_safe_size, mem=mem, cpu=cpu)
    return(r.as_dict())


def addfragtopairs(input_json):
    assert 'input_size_in_bytes' in input_json
    assert 'input_pairs' in input_json.get('input_size_in_bytes')

    cpu = 1  # very rough estimate
    mem = 1024  # very rough estimate

    # space
    insize = B2GB(input_json['input_size_in_bytes']['input_pairs'])
    outsize = insize * 2
    intersize = outsize
    total_size = insize + outsize + intersize
    total_safe_size = total_size * 2

    r = BenchmarkResult(size=total_safe_size, mem=mem, cpu=cpu)
    return(r.as_dict())


def pairs_patch(input_json):
    assert 'input_size_in_bytes' in input_json
    assert 'input_pairs' in input_json.get('input_size_in_bytes')

    cpu = 1  # very rough estimate
    mem = 1024  # very rough estimate

    # space
    insize = B2GB(input_json['input_size_in_bytes']['input_pairs'])
    outsize = insize * 2
    intersize = outsize
    total_size = insize + outsize + intersize
    total_safe_size = total_size * 2

    r = BenchmarkResult(size=total_safe_size, mem=mem, cpu=cpu)
    return(r.as_dict())


def pairsqc_single(input_json):
    assert 'input_size_in_bytes' in input_json
    assert 'input_pairs' in input_json.get('input_size_in_bytes')

    cpu = 1  # very rough estimate
    mem = 1024  # very rough estimate

    # space
    insize = B2GB(input_json['input_size_in_bytes']['input_pairs'])
    outsize = 0
    intersize = 0
    total_size = insize + outsize + intersize
    total_safe_size = total_size * 2

    r = BenchmarkResult(size=total_safe_size, mem=mem, cpu=cpu)
    return(r.as_dict())


def hi_c_processing_partb(input_json):
    assert 'input_size_in_bytes' in input_json
    assert 'input_pairs' in input_json.get('input_size_in_bytes')
    in_size = input_json['input_size_in_bytes']
    assert isinstance(in_size['input_pairs'], list)

    # cpu
    nthreads = 8  # default from cwl
    if 'parameters' in input_json:
        if 'ncores' in input_json.get('parameters'):
            nthreads = input_json.get('parameters').get('ncores')

    # space
    input_size = B2GB(sum(in_size['input_pairs']))
    out_pairs_size = input_size
    out_cool_size = input_size
    out_hic_size = input_size
    out_size = out_pairs_size + out_cool_size + out_hic_size
    total_size = input_size + out_size
    total_safe_size = total_size * 2

    # mem
    maxmem = MB2GB(14)  # default from cwl
    if 'parameters' in input_json:
        if 'maxmem' in input_json.get('parameters'):
            maxmem = input_json.get('parameters').get('maxmem')
            if 'g' in maxmem:
                maxmem = GB2MB(int(maxmem.replace('g', '')))
            elif 'm' in maxmem:
                maxmem = int(maxmem.replace('m', ''))
            else:
                raise Exception("proper maxmem string?")

    cooler_mem = GB2MB(nthreads * input_size)
    if cooler_mem > maxmem:
        mem = cooler_mem
    else:
        mem = maxmem

    r = BenchmarkResult(size=total_safe_size, mem=mem, cpu=nthreads)
    return(r.as_dict())


def hi_c_processing_partc(input_json):
    assert 'input_size_in_bytes' in input_json
    insize = input_json.get('input_size_in_bytes')
    assert 'input_cool' in insize
    assert 'input_hic' in insize

    nthreads = 1  # default value according to the cwl
    nres = 13  # default value according to the cwl
    if 'parameters' in input_json:
        if 'ncores' in input_json.get('parameters'):
            nthreads = input_json.get('parameters').get('ncores')
        if 'nres' in input_json.get('parameters'):
            nres = input_json.get('parameters').get('nres')

    input_size = insize['input_cool'] + insize['input_hic']
    out_size = input_size * nres
    inter_size = out_size
    total_size = B2GB(input_size + out_size + inter_size)
    total_safe_size = total_size * 2

    cpu = nthreads
    mem = B2MB(nthreads * input_size * 5)
    if mem < 1024:
        mem = 1024

    r = BenchmarkResult(size=total_safe_size,
                        mem=mem,
                        cpu=cpu)

    return(r.as_dict())


def hi_c_processing_bam(input_json):
    assert 'input_size_in_bytes' in input_json
    in_size = input_json.get('input_size_in_bytes')
    assert 'input_bams' in input_json.get('input_size_in_bytes')
    assert 'chromsize' in input_json.get('input_size_in_bytes')
    assert isinstance(in_size['input_bams'], list)

    # cpu
    nthreads_parse_sort = 8  # default from cwl
    nthreads_merge = 8  # default from cwl
    if 'parameters' in input_json:
        param = input_json['parameters']
        if 'nthreads_parse_sort' in param:
            nthreads_parse_sort = param['nthreads_parse_sort']
        if 'nthreads_merge' in param:
            nthreads_merge = param['nthreads_merge']

    # nthreads is the maximum of the two nthread parameters
    if nthreads_parse_sort > nthreads_merge:
        nthreads = nthreads_parse_sort
    else:
        nthreads = nthreads_merge

    bamsize = B2GB(sum(in_size['input_bams']))
    other_inputsize = B2GB(in_size.get('chromsize'))
    pairsize = bamsize / 2  # rough number
    outsize = bamsize + pairsize
    tmp_pairsamsize = bamsize * 5
    # input and output are copied once
    total_size = (bamsize + other_inputsize + outsize) * 2 + tmp_pairsamsize
    safe_total_size = total_size * 2
    mem = 2000  # very rough number

    r = BenchmarkResult(size=safe_total_size, mem=mem, cpu=nthreads)

    return(r.as_dict())


def hi_c_processing_pairs(input_json):
    assert 'input_size_in_bytes' in input_json
    assert 'input_pairs' in input_json.get('input_size_in_bytes')
    in_size = input_json['input_size_in_bytes']
    assert isinstance(in_size['input_pairs'], list)

    # cpu
    nthreads = 8  # default from cwl
    if 'parameters' in input_json:
        if 'nthreads' in input_json.get('parameters'):
            nthreads = input_json.get('parameters').get('nthreads')

    # space
    input_size = B2GB(sum(in_size['input_pairs']))
    out_size = input_size * 1.5
    intermediate_size = input_size * 10
    total_size = input_size + out_size + intermediate_size
    total_safe_size = total_size * 1.4

    # mem
    maxmem = GB2MB(14)  # default from cwl
    if 'parameters' in input_json:
        if 'maxmem' in input_json.get('parameters'):
            maxmem = input_json.get('parameters').get('maxmem')
            if 'g' in maxmem:
                maxmem = GB2MB(int(maxmem.replace('g', '')))
            elif 'm' in maxmem:
                maxmem = int(maxmem.replace('m', ''))
            else:
                raise Exception("proper maxmem string?")

    cooler_mem = GB2MB(nthreads * input_size)
    if cooler_mem > maxmem:
        mem = cooler_mem
    else:
        mem = maxmem

    r = BenchmarkResult(size=total_safe_size, mem=mem, cpu=nthreads)
    return(r.as_dict())


def hi_c_processing_pairs_nore(input_json):
    return(hi_c_processing_pairs(input_json))


def hi_c_processing_pairs_nonorm(input_json):
    return(hi_c_processing_pairs(input_json))


def hi_c_processing_pairs_nore_nonorm(input_json):
    return(hi_c_processing_pairs(input_json))


def repliseq_parta(input_json):
    assert 'input_size_in_bytes' in input_json
    assert 'fastq' in input_json.get('input_size_in_bytes')
    assert 'bwaIndex' in input_json.get('input_size_in_bytes')

    # cpu
    nthreads = 4  # default from cwl
    if 'parameters' in input_json:
        if 'nthreads' in input_json.get('parameters'):
            nthreads = input_json.get('parameters').get('nthreads')

    # space
    input_sizes = input_json.get('input_size_in_bytes')
    input_fastq = B2MB(input_sizes.get('fastq'))
    input_bwa = B2GB(input_sizes.get('bwaIndex'))
    if 'fastq2' in input_sizes: # pe
        total_space = input_fastq * 0.032 + input_bwa * 2.58
        mem = input_fastq * 8.48 + nthreads * 329 + input_bwa * 1658
    else: # se
        total_space = input_fastq * 0.018 + input_bwa * 2.54
        mem = input_fastq * 9.73 + nthreads * 221 + input_bwa * 1658

    r = BenchmarkResult(size=total_space * 1.5, mem=mem * 1.5, cpu=nthreads)

    return(r.as_dict())
