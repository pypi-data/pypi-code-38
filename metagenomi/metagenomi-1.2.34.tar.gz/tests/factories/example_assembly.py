from decimal import Decimal

assembly = {
  "associated": {
    "sequencing": [
      "PREY_SS07_USA_MGQ-read"
    ]
  },
  "created": "2018-11-18 07:17:11",
  "Mapping": [
    {
      "aligned_mapq_greaterequal_10": 51893227,
      "aligned_mapq_less_10": 40006,
      "cmd_run": "snap-aligner paired /scratch/626331aa-094e-4eaf-82e9-b7c9e1abbf11/snap /scratch/626331aa-094e-4eaf-82e9-b7c9e1abbf11/PREY_SS07_USA_MGQ-read_trim_clean.1.fastq.gz /scratch/626331aa-094e-4eaf-82e9-b7c9e1abbf11/PREY_SS07_USA_MGQ-read_trim_clean.2.fastq.gz -t 24 -o /scratch/626331aa-094e-4eaf-82e9-b7c9e1abbf11/PREY_SS07_USA_MGQ-assm_contigs_min1000.bam -F a",
      "updated": "2018-12-13 05:12:17",
      "percent_pairs": Decimal(35.97),
      "reads_mapped": {
        "fwd": "s3://metagenomi/projects/rey/reads/qc/PREY_SS07_USA_MGQ-read_trim_clean.1.fastq.gz",
        "rev": "s3://metagenomi/projects/rey/reads/qc/PREY_SS07_USA_MGQ-read_trim_clean.2.fastq.gz"
      },
      "reads_per_sec": 418316,
      "ref": "s3://metagenomi/projects/rey/assembly/PREY_SS07_USA_MGQ-assm/PREY_SS07_USA_MGQ-assm_contigs_min1000.fa",
      "seed_size": 22,
      "time_in_aligner_seconds": 294,
      "too_short_OR_too_many_NNs": 130068,
      "total_bases": 949117909,
      "total_reads": 123115638,
      "unaligned": 71052337
    }
  ],
  "Megahit": {
    "sequence_parameters": {
        "length": [92424, 90880, 84974, 79424, 77093, 67199, 64994, 62028, 60450, 58891],
        "gc": [Decimal(38.59), Decimal(40.07), Decimal(40.22), Decimal(38.61),
               Decimal(40.27), Decimal(30.73), Decimal(39.99), Decimal(40.39),
               Decimal(39.57), Decimal(40.25)],
        "non_ns": [100, 100, 100, 100, 100, 100, 100, 100, 100, 100],
        "description": ["flag=1 multi=10.0191 len=92424 read_count_6656",
                        "flag=1 multi=10.1942 len=90880 read_count_6840",
                        "flag=1 multi=10.7520 len=84974 read_count_6511",
                        "flag=1 multi=11.2215 len=79424 read_count_6502",
                        "flag=0 multi=11.3333 len=77093 read_count_6047",
                        "flag=1 multi=8.7932 len=67199 read_count_4782",
                        "flag=0 multi=9.7262 len=64994 read_count_4712",
                        "flag=0 multi=11.1837 len=62028 read_count_5052",
                        "flag=0 multi=10.9944 len=60450 read_count_5007",
                        "flag=1 multi=9.5340 len=58891 read_count_4311"],
        "seq_num": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "sequence": ["PREY_ES05_USA_MGQ-assm_1183167",
                     "PREY_ES05_USA_MGQ-assm_139509",
                     "PREY_ES05_USA_MGQ-assm_655643",
                     "PREY_ES05_USA_MGQ-assm_399045",
                     "PREY_ES05_USA_MGQ-assm_1163425",
                     "PREY_ES05_USA_MGQ-assm_240947",
                     "PREY_ES05_USA_MGQ-assm_859467",
                     "PREY_ES05_USA_MGQ-assm_1538509",
                     "PREY_ES05_USA_MGQ-assm_1451674",
                     "PREY_ES05_USA_MGQ-assm_13022"]
        },
    "length_distribution": {
        "num_sequences": [0, 0, 293, 135328, 2036, 281, 75, 13],
        "num_sequences_percent": [Decimal(0.0), Decimal(0.0), Decimal(0.21),
                                  Decimal(98.04), Decimal(1.47), Decimal(0.2),
                                  Decimal(0.05), Decimal(0.0)],
        "num_bps": [0, 0, 293000, 216143943, 13161284, 3691810, 2188891, 9029],
        "num_bps_percent": [Decimal(0.0), Decimal(0.0), Decimal(0.12),
                            Decimal(91.43), Decimal(5.56), Decimal(1.56),
                            Decimal(0.92), Decimal(0.38)],
        "start": [0, 100, 500, 1000, 5000, 10000, 20000, 50000],
        "end": [100, 500, 1000, 5000, 10000, 20000, 50000, 92424]
        },
    "total_seqs": 138026,
    "total_bps": 236381137,
    "n50": 1668,
    "avg_seq_len": Decimal(1712.58)
  },

  "mgid": "PREY_SS07_USA_MGQ-assm",
  "mgtype": "assembly",
  "project": "PREY",
  "s3path": "s3://metagenomi/projects/rey/assembly/PREY_SS07_USA_MGQ-assm/PREY_SS07_USA_MGQ-assm_contigs_min1000.fa",
  "alt_id": "None"
  }
