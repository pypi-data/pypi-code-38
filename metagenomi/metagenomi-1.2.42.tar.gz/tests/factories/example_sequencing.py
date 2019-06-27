from decimal import Decimal

sequencing = {
  "associated": {
    "assembly": [
      "PREY_SS13_USA_MGQ-assm"
    ],
    "sample": [
      "PREY_SS13_USA_MGS-samp"
    ]
  },
  "created":"2019-01-16 16:22:05",
  "job_id":"jobid123",
  "Bbmap": {
    "trimmed_reads": {
      "fwd": "s3://metagenomi/projects/rey/reads/qc/PREY_ES01_USA_MGQ-read_trim_clean.1.fastq.gz",
      "rev": "s3://metagenomi/projects/rey/reads/qc/PREY_ES01_USA_MGQ-read_trim_clean.2.fastq.gz"
    },
    "cmd_run": "adapter_removal,contaminant_removal,quality_trimming",
    "updated": "2019-01-16 16:22:05",
    "total_bases": 17765359800,
    "total_reads": 118435732,

    "adapter_removal": {
      "cmd_run": "/tmp/bbmap/bbduk.sh ref=/tmp/bbmap/resources/adapters.fa k=23 mink=11 hdist=1 tbo tpe ktrim=r ftm=5 -in1=/scratch/9f88a387-d7af-4932-a827-e8a1ea6e7e66/SS_13_DNA_Q.1.fastq.gz -out1=/scratch/9f88a387-d7af-4932-a827-e8a1ea6e7e66/SS_13_DNA_Q.1.fastq.g_trim.fastq.gz -in2=/scratch/9f88a387-d7af-4932-a827-e8a1ea6e7e66/SS_13_DNA_Q.2.fastq.gz -out2=/scratch/9f88a387-d7af-4932-a827-e8a1ea6e7e66/SS_13_DNA_Q.2.fastq.g_trim.fastq.gz t=16",
      "ftrimmed_reads": 0,
      "ktrimmed_reads": 1434068,
      "total_removed_reads": 47148,
      "trimmed_by_overlap_reads": 357540
      },

    "contaminant_removal": {
      "cmd_run": "/tmp/bbmap/bbduk.sh ref=/tmp/bbmap/resources/phix174_ill.ref.fa.gz,/tmp/bbmap/resources/sequencing_artifacts.fa.gz k=31 hdist=1 -in1=/scratch/9f88a387-d7af-4932-a827-e8a1ea6e7e66/SS_13_DNA_Q.1.fastq.g_trim.fastq.gz -out1=/scratch/9f88a387-d7af-4932-a827-e8a1ea6e7e66/SS_13_DNA_Q.1.fastq.g_trim.fastq.g_trim_clean.fastq.gz -in2=/scratch/9f88a387-d7af-4932-a827-e8a1ea6e7e66/SS_13_DNA_Q.2.fastq.g_trim.fastq.gz -out2=/scratch/9f88a387-d7af-4932-a827-e8a1ea6e7e66/SS_13_DNA_Q.2.fastq.g_trim.fastq.g_trim_clean.fastq.gz t=16",
      "contaminants": 1672,
      "total_removed_reads": 1672
      },
    "quality_trimming": {
      "cmd_run": "/tmp/bbmap/bbduk.sh qtrim=f trimq=6 -in1=/scratch/9f88a387-d7af-4932-a827-e8a1ea6e7e66/SS_13_DNA_Q.1.fastq.g_trim.fastq.g_trim_clean.fastq.gz -out1=/scratch/9f88a387-d7af-4932-a827-e8a1ea6e7e66/SS_13_DNA_Q.1.fastq.g_trim.fastq.g_trim_clean.fastq.g_trim_clean_qual.fastq.gz -in2=/scratch/9f88a387-d7af-4932-a827-e8a1ea6e7e66/SS_13_DNA_Q.2.fastq.g_trim.fastq.g_trim_clean.fastq.gz -out2=/scratch/9f88a387-d7af-4932-a827-e8a1ea6e7e66/SS_13_DNA_Q.2.fastq.g_trim.fastq.g_trim_clean.fastq.g_trim_clean_qual.fastq.gz t=16",
      "total_removed_reads":0
      }
  },

  "SequencingInfo": {
    "cmd_run": "None",
    "updated": "2019-01-17 12:53:46",
    "avg_length": 150,
    "bases": 17765359800,
    "insert_size": "None",
    "library_layout": "PAIRED",
    "library_selection": "RANDOM",
    "library_source": "METAGENOMIC",
    "library_strategy": "WGS",
    "model": "Hi-Seq4000",
    "platform": "ILLUMINA",
    "raw_read_paths": {
      "fwd": "s3://metagenomi/projects/rey/reads/raw/SS_13_DNA_Q.1.fastq.gz",
      "rev": "s3://metagenomi/projects/rey/reads/raw/SS_13_DNA_Q.2.fastq.gz"
    },
    "sample_name": "SS13",
    "size_mb": {
      "fwd": Decimal(5081.223498),
      "rev": Decimal(6165.987524)
    },
    "spots": 118435732,
    "spots_with_mates": "None"
  },
  "mgid": "PREY_SS13_USA_MGQ-read",
  "mgtype": "sequencing",
  "project": "PREY",
  "Nonpareil": {
    "updated": "2019-01-17 12:30:50",
    "c": Decimal(9.968215e-01),
    "cmd_run": "/tmp/nonpareil-3.303-Linux_x86_64 -s /scratch/1f3b866b-4857-4eb5-b145-f58fc287e8f2/PREY_SS13_USA_MGQ-read_trim_clean.1.fastq.gz -b /scratch/1f3b866b-4857-4eb5-b145-f58fc287e8f2/nonpareil -T alignment -f fastq -X 1000 -k 24 -L 70 -R 1024 -t 16",
    "diversity": Decimal(1.330950e+01),
    "input": "s3://metagenomi/projects/rey/reads/qc/PREY_SS13_USA_MGQ-read_trim_clean.1.fastq.gz",
    "kappa": Decimal(9.963300e-01),
    "lr": Decimal(1.343124e+09),
    "lr_star": Decimal(6.918910e+06),
    "modelr": Decimal(9.964438e-01),
    "output": "s3://metagenomi/projects/rey/reads/qc/nonpareil/PREY_SS13_USA_MGQ-read_trim_clean_nonpareil",
    "pdf": "s3://metagenomi/projects/rey/reads/qc/nonpareil/PREY_SS13_USA_MGQ-read_trim_clean_nonpareil.pdf",
    "tsv": "s3://metagenomi/projects/rey/reads/qc/nonpareil/PREY_SS13_USA_MGQ-read_trim_clean_nonpareil.tsv"
  },
  "s3path": {
    "fwd":"s3://metagenomi/projects/rey/reads/qc/PREY_SS13_USA_MGQ-read_trim_clean.1.fastq.gz",
    "rev":"s3://metagenomi/projects/rey/reads/qc/PREY_SS13_USA_MGQ-read_trim_clean.2.fastq.gz"
  },
  "alt_id": "None"
}
