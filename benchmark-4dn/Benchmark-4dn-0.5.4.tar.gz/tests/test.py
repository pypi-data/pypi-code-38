import unittest
from Benchmark import run as B
from Benchmark import classes as C
from Benchmark.byteformat import GB2B, MB2B


class TestGetOptimalInstanceType(unittest.TestCase):
    def test_get_optimal_instance_type1(self):
        res = C.get_optimal_instance_type()
        assert 'recommended_instance_type' in res
        assert res['recommended_instance_type'] == 't3.nano'

    def test_get_optimal_instance_type2(self):
        res = C.get_optimal_instance_type(cpu=32, mem_in_gb=16)
        assert 'recommended_instance_type' in res
        assert res['recommended_instance_type'] == 'c5.9xlarge'


class TestBenchmark(unittest.TestCase):
    def test_repliseq(self):
        print("repliseq se")
        input_json = {'input_size_in_bytes': {'fastq': MB2B(270),
                                              'bwaIndex': GB2B(3.21)},
                      'parameters': {'nthreads': 4}}
        res = B.benchmark('repliseq-parta', input_json)
        print(res)
        assert 'aws' in res
        assert 'recommended_instance_type' in res['aws']
        assert res['aws']['recommended_instance_type'] == 't3.xlarge'

    def test_repliseq2(self):
        print("repliseq pe")
        input_json = {'input_size_in_bytes': {'fastq': MB2B(270),
                                              'fastq2': MB2B(270),
                                              'bwaIndex': GB2B(3.21)},
                      'parameters': {'nthreads': 4}}
        res = B.benchmark('repliseq-parta', input_json)
        print(res)
        assert 'aws' in res
        assert 'recommended_instance_type' in res['aws']
        assert res['aws']['recommended_instance_type'] == 't3.xlarge'

    def test_mergebed(self):
        print("mergebed")
        input_sizes = {'input_bed': [400000000, 500000000]}
        res = B.benchmark('mergebed', {'input_size_in_bytes': input_sizes})
        print(res)
        assert 'aws' in res
        assert 'recommended_instance_type' in res['aws']
        assert res['aws']['recommended_instance_type'] == 't3.micro'

    def test_benchmark_atacseq_aln(self):
        print("testing atacseq-aln")
        input_sizes = {'atac.fastqs': [1200000000, 1200000000, 1500000000, 1500000000],
                       'atac.bowtie2_idx_tar': 5000000000}
        res = B.benchmark('encode-atacseq-aln',
                          {'input_size_in_bytes': input_sizes,
                           'parameters': {'atac.bowtie2.cpu': 4, 'atac.paired_end': True}})
        print(res)
        assert 'aws' in res
        assert 'recommended_instance_type' in res['aws']
        assert res['aws']['recommended_instance_type'] == 'c5.xlarge'

    def test_benchmark_atacseq_postaln(self):
        print("testing atacseq-postaln")
        input_sizes = {'atac.tas': [827000000]}
        res = B.benchmark('encode-atacseq-postaln',
                          {'input_size_in_bytes': input_sizes})
        print(res)
        assert 'aws' in res
        assert 'recommended_instance_type' in res['aws']
        assert res['aws']['recommended_instance_type'] == 'c5.4xlarge'

    def test_benchmark_atacseq(self):
        print("testing atacseq")
        input_sizes = {'atac.fastqs': [2000000000, 3000000000],
                       'atac.bowtie2_idx_tar': 5000000000}
        res = B.benchmark('encode-atacseq',
                          {'input_size_in_bytes': input_sizes,
                           'parameters': {'atac.bowtie2.cpu': 4}})
        assert 'aws' in res
        assert 'recommended_instance_type' in res['aws']
        assert res['aws']['recommended_instance_type'] == 't3.2xlarge'
        assert res['min_CPU'] == 6
        assert int(res['total_size_in_GB']) == 55

    def test_benchmark_chipseq_aln_chip(self):
        print("testing chipseq")
        input_sizes = {'chip.fastqs': [2000000000, 3000000000],
                       'chip.bwa_idx_tar': 5000000000}
        res = B.benchmark('encode-chipseq-aln-chip',
                          {'input_size_in_bytes': input_sizes,
                           'parameters': {'chip.bwa.cpu': 16}})
        assert 'aws' in res
        assert 'recommended_instance_type' in res['aws']
        assert res['aws']['recommended_instance_type'] == 'c5.4xlarge'

    def test_benchmark_chipseq_aln_ctl(self):
        print("testing chipseq")
        input_sizes = {'chip.ctl_fastqs': [3000000000, 2000000000],
                       'chip.bwa_idx_tar': 5000000000}
        res = B.benchmark('encode-chipseq-aln-ctl',
                          {'input_size_in_bytes': input_sizes,
                           'parameters': {'chip.bwa_ctl.cpu': 16}})
        assert 'aws' in res
        assert 'recommended_instance_type' in res['aws']
        assert res['aws']['recommended_instance_type'] == 'c5.4xlarge'

    def test_benchmark_chipseq_postaln(self):
        print("testing chipseq")
        input_sizes = {'chip.tas': [2000000000, 3000000000],
                       'chip.ctl_tas': [3000000000, 2000000000],
                       'chip.bam2ta_no_filt_R1.ta': [5000000000, 6000000000]}
        res = B.benchmark('encode-chipseq-postaln',
                          {'input_size_in_bytes': input_sizes,
                           'parameters': {'chip.spp_cpu': 4}})
        assert 'aws' in res
        assert 'recommended_instance_type' in res['aws']
        assert res['aws']['recommended_instance_type'] == 'c5.4xlarge'

    def test_benchmark_chipseq(self):
        print("testing chipseq")
        input_sizes = {'chip.fastqs': [2000000000, 3000000000],
                       'chip.ctl_fastqs': [3000000000, 2000000000],
                       'chip.bwa_idx_tar': 5000000000}
        res = B.benchmark('encode-chipseq',
                          {'input_size_in_bytes': input_sizes})
        print(res)
        assert 'aws' in res
        assert 'recommended_instance_type' in res['aws']
        assert res['aws']['recommended_instance_type'] == 'c5.4xlarge'

    def test_benchmark1(self):
        res = B.benchmark('md5',
                          {'input_size_in_bytes': {'input_file': 200000000}})
        assert 'aws' in res
        assert 'recommended_instance_type' in res['aws']
        assert res['aws']['recommended_instance_type'] == 't3.micro'
        print(res)

    def test_benchmark2(self):
        res = B.benchmark('fastqc-0-11-4-1',
                          {'input_size_in_bytes': {'input_fastq': 20000000000},
                           'parameters': {'threads': 2}})
        assert 'aws' in res
        assert 'recommended_instance_type' in res['aws']
        assert res['aws']['recommended_instance_type'] == 't3.micro'
        print(res)

    def test_benchmark3(self):
        input_json = {'input_size_in_bytes': {'fastq1': 93520000,
                                              'fastq2': 97604000,
                                              'bwa_index': 3364568000},
                      'parameters': {'nThreads': 4}}
        res = B.benchmark('bwa-mem', input_json)
        assert 'aws' in res
        assert 'recommended_instance_type' in res['aws']
        assert res['aws']['recommended_instance_type'] == 't3.xlarge'
        print(res)

    def test_benchmark4(self):
        res = B.benchmark('pairsam-parse-sort',
                          {'input_size_in_bytes': {'bam': 1000000000},
                           'parameters': {'nThreads': 16}})
        assert 'aws' in res
        assert 'recommended_instance_type' in res['aws']
        assert res['aws']['recommended_instance_type'] == 'c5.9xlarge'
        print(res)

    def test_benchmark5(self):
        input_json = {'input_size_in_bytes': {'input_pairsams': [1000000000,
                                                                 2000000000,
                                                                 3000000000]},
                      'parameters': {'nThreads': 32}}
        res = B.benchmark('pairsam-merge', input_json)
        assert 'aws' in res
        assert 'recommended_instance_type' in res['aws']
        assert res['aws']['recommended_instance_type'] == 'c5.9xlarge'
        print(res)

    def test_benchmark6(self):
        input_json = {'input_size_in_bytes': {'input_pairsam': 1000000000}}
        res = B.benchmark('pairsam-markasdup', input_json)
        print(res)
        assert 'aws' in res
        assert 'recommended_instance_type' in res['aws']
        assert res['aws']['recommended_instance_type'] == 'r5a.large'

    def test_benchmark7(self):
        input_json = {'input_size_in_bytes': {'input_pairsam': 1000000000}}
        res = B.benchmark('pairsam-filter', input_json)
        assert 'aws' in res
        assert 'recommended_instance_type' in res['aws']
        assert res['aws']['recommended_instance_type'] == 't3.xlarge'

    def test_benchmark8(self):
        input_json = {'input_size_in_bytes': {'input_pairs': 1000000000}}
        res = B.benchmark('addfragtopairs', input_json)
        assert 'aws' in res
        assert 'recommended_instance_type' in res['aws']
        assert res['aws']['recommended_instance_type'] == 't3.micro'

    def test_benchmark9(self):
        input_json = {'input_size_in_bytes': {'input_pairs': [1000000000,
                                                              2000000000,
                                                              3000000000]},
                      'parameters': {'ncores': 16,
                                     'maxmem': '1900g'}}
        res = B.benchmark('hi-c-processing-partb', input_json)
        assert 'aws' in res
        assert 'recommended_instance_type' in res['aws']
        assert res['aws']['recommended_instance_type'] == 'x1.32xlarge'

    def test_benchmark10(self):
        input_json = {'input_size_in_bytes': {'input_pairs': 1000000000}}
        res = B.benchmark('pairs-patch', input_json)
        print(res)
        assert 'aws' in res
        assert 'recommended_instance_type' in res['aws']
        assert res['aws']['recommended_instance_type'] == 't3.micro'

    def test_benchmark11(self):
        input_json = {'input_size_in_bytes': {'input_cool': 1000000000,
                                              'input_hic': 2000000000},
                      'parameters': {'ncores': 1}}
        res = B.benchmark('hi-c-processing-partc', input_json)
        print('hi-c-processing-partc')
        print(res)
        assert 'aws' in res
        assert 'recommended_instance_type' in res['aws']
        assert res['aws']['recommended_instance_type'] == 'r5a.large'

    def test_benchmark12(self):
        input_sizes = {'input_bams': [1000000000, 2000000000],
                       'chromsize': 200000}
        input_json = {'input_size_in_bytes': input_sizes,
                      'parameters': {'nthreads_parse_sort': 1,
                                     'nthreads_merge': 8}}
        res = B.benchmark('hi-c-processing-bam', input_json)
        print('hi-c-processing-bam')
        print("benchmark12")
        print(res)
        assert 'aws' in res
        assert 'recommended_instance_type' in res['aws']
        assert res['aws']['recommended_instance_type'] == 't3.2xlarge'
        assert res['min_CPU'] == 8

    def test_benchmark13(self):
        input_json = {'input_size_in_bytes': {'input_pairs': [1000000000,
                                                              2000000000,
                                                              3000000000]},
                      'parameters': {'nthreads': 8,
                                     'maxmem': '32g'}}
        res = B.benchmark('hi-c-processing-pairs', input_json)
        print('hi-c-processing-pairs')
        print("benchmark13")
        print(res)
        assert 'aws' in res
        assert res['min_CPU'] == 8
        assert 'recommended_instance_type' in res['aws']
        assert res['aws']['recommended_instance_type'] == 'r5a.2xlarge'

    def test_benchmark_none1(self):
        input_json = {'input_size_in_bytes': {'fastq1': 93520,
                                              'fastq2': 97604,
                                              'bwa_index': 3364568}}
        with self.assertRaises(B.AppNameUnavailableException):
            B.benchmark('some_weird_name', input_json, raise_error=True)

    def test_benchmark_none2(self):
        input_json = {'input_size_in_bytes': {'fastq1': 93520,
                                              'fastq2': 97604,
                                              'bwa_index': 3364568}}
        res = B.benchmark('some_weird_name', input_json)
        assert res is None

    def test_benchmark_insulator_score_caller(self):
        print("insulator-score-caller")
        input_json = {'input_size_in_bytes': {'mcoolfile': 32000000000}}
        res = B.benchmark('insulator-score-caller', input_json)
        print(res)
        assert 'aws' in res
        assert 'recommended_instance_type' in res['aws']
        assert res['aws']['recommended_instance_type'] == 't3.small'


class TestGetInstanceList(unittest.TestCase):
    def test_instance_list(self):
        res = C.instance_list(exclude_a1=True)
        # we should have quite some instaces in the filter
        assert len(res) > 50
        # we should have certain keys in each dictionary
        for a_field in ['cost_in_usd', 'mem_in_gb', 'cpu', 'instance_type',
                        'EBS_optimized', 'EBS_optimization_surcharge']:
            assert a_field in res[0]
        # no a1 instance should be in the list
        a1_instances = [i for i in res if i['instance_type'].startswith('a1')]
        assert not a1_instances
        # let's test the other way around
        res_a1 = C.instance_list(exclude_a1=False)
        a1_instances = [i for i in res_a1 if i['instance_type'].startswith('a1')]
        assert a1_instances

    def test_get_instance_types(self):
        res = C.get_instance_types(cpu=10, mem_in_gb=50)
        # make sure we have something in the results
        assert res
        # default ranking is by cost, assert cheapest is the first one
        costs = [i['cost_in_usd'] for i in res]
        min_cost = min(costs)
        max_cost = max(costs)
        assert res[0]['cost_in_usd'] == min_cost
        assert res[-1]['cost_in_usd'] == max_cost
        # limit the result length
        res = C.get_instance_types(cpu=10, mem_in_gb=50, top=3)
        assert len(res) == 3
        # if top is more then the result, it should return all
        res = C.get_instance_types(cpu=10, mem_in_gb=50, top=300)
        assert len(res) < 300


if __name__ == '__main__':
    unittest.main()
