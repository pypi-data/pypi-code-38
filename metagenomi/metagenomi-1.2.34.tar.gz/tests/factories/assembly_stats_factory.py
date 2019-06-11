import factory

from decimal import Decimal

from metagenomi.tasks.assemblystats import Assembly_stats


class Assembly_statsFactory(factory.Factory):
    class Meta:
        model = Assembly_stats
    mgid = 'CODE_NUM_CNTY'
    cmd_run = 'a assembly stats command string!'
    job_id = factory.Faker('pyint')
    total_seqs = factory.Faker('pyint')
    total_bps = factory.Faker('pyint')
    n50 = factory.Faker('pyint')
    avg_seq_len = Decimal(1712.58)
    sequence_parameters = {
        'length': [92424, 90880, 84974, 79424, 77093, 67199, 64994, 62028, 60450, 58891],
        'gc': [Decimal(38.59), Decimal(40.07), Decimal(40.22), Decimal(38.61),
               Decimal(40.27), Decimal(30.73), Decimal(39.99), Decimal(40.39),
               Decimal(39.57), Decimal(40.25)],
        'non_ns': [100, 100, 100, 100, 100, 100, 100, 100, 100, 100],
        'description': ['flag=1 multi=10.0191 len=92424 read_count_6656',
                        'flag=1 multi=10.1942 len=90880 read_count_6840',
                        'flag=1 multi=10.7520 len=84974 read_count_6511',
                        'flag=1 multi=11.2215 len=79424 read_count_6502',
                        'flag=0 multi=11.3333 len=77093 read_count_6047',
                        'flag=1 multi=8.7932 len=67199 read_count_4782',
                        'flag=0 multi=9.7262 len=64994 read_count_4712',
                        'flag=0 multi=11.1837 len=62028 read_count_5052',
                        'flag=0 multi=10.9944 len=60450 read_count_5007',
                        'flag=1 multi=9.5340 len=58891 read_count_4311'],
        'seq_num': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'sequence': ['PREY_ES05_USA_MGQ-assm_1183167',
                     'PREY_ES05_USA_MGQ-assm_139509',
                     'PREY_ES05_USA_MGQ-assm_655643',
                     'PREY_ES05_USA_MGQ-assm_399045',
                     'PREY_ES05_USA_MGQ-assm_1163425',
                     'PREY_ES05_USA_MGQ-assm_240947',
                     'PREY_ES05_USA_MGQ-assm_859467',
                     'PREY_ES05_USA_MGQ-assm_1538509',
                     'PREY_ES05_USA_MGQ-assm_1451674',
                     'PREY_ES05_USA_MGQ-assm_13022']
    }
    length_distribution = {
        'num_sequences': [0, 0, 293, 135328, 2036, 281, 75, 13],
        'num_sequences_percent': [Decimal(0.0), Decimal(0.0), Decimal(0.21),
                                  Decimal(98.04), Decimal(1.47), Decimal(0.2),
                                  Decimal(0.05), Decimal(0.0)],
        'num_bps': [0, 0, 293000, 216143943, 13161284, 3691810, 2188891, 9029],
        'num_bps_percent': [Decimal(0.0), Decimal(0.0), Decimal(0.12),
                            Decimal(91.43), Decimal(5.56), Decimal(1.56),
                            Decimal(0.92), Decimal(0.38)],
        'start': [0, 100, 500, 1000, 5000, 10000, 20000, 50000],
        'end': [100, 500, 1000, 5000, 10000, 20000, 50000, 92424]
    }
