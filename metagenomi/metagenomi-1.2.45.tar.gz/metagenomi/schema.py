
<<<<<<< HEAD

from decimal import Decimal
from cerberus import Validator
from cerberus import TypeDefinition
import datetime
import doctest

TIME_FMT = '%Y-%m-%d %H:%M:%S'

base = {'mg_identifier': {'type': 'string'},
        'cmd_run': {'required': True, 'type': 'string'},
        'updated': {'required': True, 'type': 'datetime'}}

decimal_type = TypeDefinition('decimal', (Decimal,), ())
Validator.types_mapping['decimal'] = decimal_type


def get_mapping_schema():
    decimal_type = TypeDefinition('decimal', (Decimal,), ())
    Validator.types_mapping['decimal'] = decimal_type

    schema = {'aligned_mapq_greaterequal_10': {'required': True, 'type': 'integer'},
                'aligned_mapq_less_10': {'required': True, 'type': 'integer'},
                'percent_pairs': {'required': True, 'type': 'decimal'},
                'reads_per_sec': {'required': True, 'type': 'integer'},
                'seed_size': {'required': True, 'type': 'integer'},
                'time_in_aligner_seconds': {'required': True, 'type': 'integer'},
                'too_short_or_too_many_NNs': {'required': True, 'type': 'integer'},
                'total_bases': {'required': True, 'type': 'integer'},
                'total_reads': {'required': True, 'type': 'integer'},
                'unaligned': {'required': True, 'type': 'integer'},
                'reads_mapped': {'required': True, 'type': 'list'},
                'reference': {'required': True, 'type': 'string'}
                }

    return({**base, **schema})


def get_nonpareil_schema():
    schema = {'c': {'type': 'decimal'},
                'diversity': {'required': True, 'type': 'decimal'},
                'input': {'required': True, 'type': 'string'},
                'kappa': {'required': True, 'type': 'decimal'},
                'lr': {'required': True, 'type': 'decimal'},
                'lrstar': {'required': True, 'type': 'decimal'},
                'modelr': {'required': True, 'type': 'decimal'},
                'output': {'required': True, 'type': 'string'},
                'pdf': {'required': True, 'type': 'string'},
                'tsv': {'required': True, 'type': 'string'}}

    return({**base, **schema})


def get_megahit_schema():
    schema = {'avg_seqeunce_length': {'required': True, 'type': 'decimal'},
                'n50': {'required': True, 'type': 'integer'},
                'seq_params': {'required': True, 'type': 'dict'},
                'length_distribution': {'required': True, 'type': 'dict'},
                'total_bps': {'required': True, 'type': 'integer'},
                'total_seqs': {'required': True, 'type': 'integer'},
                'longest_contig': {'type': 'string'}}

    return({**base, **schema})


def get_megahit_schema():
    schema = {'avg_seqeunce_length': {'required': True, 'type': 'decimal'},
                'n50': {'required': True, 'type': 'integer'},
                'seq_params': {'required': True, 'type': 'dict'},
                'length_distribution': {'required': True, 'type': 'dict'},
                'total_bps': {'required': True, 'type': 'integer'},
                'total_seqs': {'required': True, 'type': 'integer'},
                'longest_contig': {'type': 'string'}}

    return({**base, **schema})


def get_megahit_test():

    seq_params = {'length': {'PREY_SS25_USA_MGQ-assm_1307333': 316406, 'PREY_SS25_USA_MGQ-assm_1431964': 230898, 'PREY_SS25_USA_MGQ-assm_1458387': 222546, 'PREY_SS25_USA_MGQ-assm_1485461': 260194, 'PREY_SS25_USA_MGQ-assm_245903': 220698, 'PREY_SS25_USA_MGQ-assm_509001': 341352, 'PREY_SS25_USA_MGQ-assm_594224': 307369, 'PREY_SS25_USA_MGQ-assm_757532': 225381, 'PREY_SS25_USA_MGQ-assm_889155': 244256, 'PREY_SS25_USA_MGQ-assm_969925': 224930}, 'description': {'PREY_SS25_USA_MGQ-assm_1307333': 'flag=0 multi=16.2256 len=316406', 'PREY_SS25_USA_MGQ-assm_1431964': 'flag=0 multi=15.3303 len=230898', 'PREY_SS25_USA_MGQ-assm_1458387': 'flag=0 multi=18.4303 len=222546', 'PREY_SS25_USA_MGQ-assm_1485461': 'flag=0 multi=19.2861 len=260194', 'PREY_SS25_USA_MGQ-assm_245903': 'flag=0 multi=29.0965 len=220698', 'PREY_SS25_USA_MGQ-assm_509001': 'flag=0 multi=28.1719 len=341352', 'PREY_SS25_USA_MGQ-assm_594224': 'flag=0 multi=15.1067 len=307369', 'PREY_SS25_USA_MGQ-assm_757532': 'flag=0 multi=28.9972 len=225381', 'PREY_SS25_USA_MGQ-assm_889155': 'flag=3 multi=75.0003 len=244256', 'PREY_SS25_USA_MGQ-assm_969925': 'flag=0 multi=29.2787 len=224930'}, 'seq_num': {'PREY_SS25_USA_MGQ-assm_1307333': '2', 'PREY_SS25_USA_MGQ-assm_1431964': '6', 'PREY_SS25_USA_MGQ-assm_1458387': '9', 'PREY_SS25_USA_MGQ-assm_1485461': '4', 'PREY_SS25_USA_MGQ-assm_245903': '10', 'PREY_SS25_USA_MGQ-assm_509001': '1', 'PREY_SS25_USA_MGQ-assm_594224': '3', 'PREY_SS25_USA_MGQ-assm_757532': '7', 'PREY_SS25_USA_MGQ-assm_889155': '5', 'PREY_SS25_USA_MGQ-assm_969925': '8'}, 'Non-Ns': {'PREY_SS25_USA_MGQ-assm_1307333': '100', 'PREY_SS25_USA_MGQ-assm_1431964': '100', 'PREY_SS25_USA_MGQ-assm_1458387': '100', 'PREY_SS25_USA_MGQ-assm_1485461': '100', 'PREY_SS25_USA_MGQ-assm_245903': '100', 'PREY_SS25_USA_MGQ-assm_509001': '100', 'PREY_SS25_USA_MGQ-assm_594224': '100', 'PREY_SS25_USA_MGQ-assm_757532': '100', 'PREY_SS25_USA_MGQ-assm_889155': '100', 'PREY_SS25_USA_MGQ-assm_969925': '100'}, 'G+C': {'PREY_SS25_USA_MGQ-assm_1307333': 41.55, 'PREY_SS25_USA_MGQ-assm_1431964': 39.82, 'PREY_SS25_USA_MGQ-assm_1458387': 55.02, 'PREY_SS25_USA_MGQ-assm_1485461': 40.09, 'PREY_SS25_USA_MGQ-assm_245903': 37.4, 'PREY_SS25_USA_MGQ-assm_509001': 38.22, 'PREY_SS25_USA_MGQ-assm_594224': 40.35, 'PREY_SS25_USA_MGQ-assm_757532': 37.83, 'PREY_SS25_USA_MGQ-assm_889155': 33.61, 'PREY_SS25_USA_MGQ-assm_969925': 37.6}}

    len_dist = {'num_bps_percent': {'0': 0.0, '1': 23.19, '2': 23.78, '3': 29.98, '4': 8.58, '5': 6.62, '6': 4.92, '7': 1.95, '8': 0.93}, 'num_sequences': {'0': 0, '1': 840986, '2': 477545, '3': 222230, '4': 17054, '5': 6647, '6': 2350, '7': 406, '8': 89}, 'num_bps': {'0': 0, '1': 316476217, '2': 324500060, '3': 409006853, '4': 117102312, '5': 90334963, '6': 67218581, '7': 26728086, '8': 12791882}, 'num_sequences_percent': {'0': 0.0, '1': 53.65, '2': 30.46, '3': 14.17, '4': 1.08, '5': 0.42, '6': 0.14, '7': 0.02, '8': 0.0}, 'start': {'0': 0, '1': 100, '2': 500, '3': 1000, '4': 5000, '5': 10000, '6': 20000, '7': 50000, '8': 100000}, 'end': {'0': 100, '1': 500, '2': 1000, '3': 5000, '4': 10000, '5': 20000, '6': 50000, '7': 100000, '8': 341352}}

    return {'avg_seqeunce_length': Decimal(1.0),
            'n50': 44,
            'seq_params': seq_params,
            'length_distribution': len_dist,
            'total_bps': 1000,
            'total_seqs': 10,
            'longest_contig': 'contig1'}


def get_mapping_test():
    return {'aligned_mapq_greaterequal_10': 44,
             'aligned_mapq_less_10': 4,
             'percent_pairs': Decimal(1.0),
             'reads_per_sec': 33,
             'seed_size': 1,
             'time_in_aligner_seconds': 11,
             'too_short_or_too_many_NNs': 2,
             'total_bases': 1,
             'total_reads': 55,
             'unaligned': 2,
             'reads_mapped': [{'fwd': 's3://forward/read.fa'},
                              {'rev': 's3://forward/read.fa'}],
             'reference': 's3://reference/contigs.fa'}

def test():
    '''
    ## Megahit tests
    >>> v = Validator(get_megahit_schema())
    >>> d = get_megahit_test()
    >>> v.validate(d)
    False
    >>> v.errors
    {'cmd_run': ['required field'], 'updated': ['required field']}
    >>> d['cmd_run'] = 'dummy cmd'
    >>> v.validate(d)
    False
    >>> v.errors
    {'updated': ['required field']}
    >>> d['updated'] = datetime.datetime.now()
    >>> v.validate(d)
    True
    >>> d['updated'] = 'String'
    >>> d['total_seqs'] = 1.54
    >>> v.validate(d)
    False
    >>> v.errors
    {'total_seqs': ['must be of integer type'], 'updated': ['must be of datetime type']}


    ## Mapping tests
    >>> v = Validator(get_mapping_schema())
    >>> d = get_mapping_test()
    >>> v.validate(d)
    False
    >>> d['cmd_run'] = 'dummy cmd'
    >>> d['updated'] = datetime.datetime.now()
    >>> v.validate(d)
    True

    '''
    pass

if __name__=='__main__':

    doctest.testmod()
=======
# s3regex = "^s3:\/\/.+"

'''
BASE
'''

base = {
          "mg_identifier": {
            "type": "string",
            "regex": "^s"
          },
          "cmd_run": {
            "required": True,
            "type": "string"
          },
          "updated": {
            "required": True,
            "type": "datestring"
          }
        }

'''
BBMAP
'''

bbmap = {
    'trimmed_reads': {
        'required': True,
        'type': 'dict',
        'schema': {
            'fwd': {'type': 'string', 'required': True, 'regex': '^s3:\/\/.+'},
            'rev': {'type': 'string', 'required': True, 'regex': '^s3:\/\/.+'}
            }
    },
    'total_bases': {'required': True, 'type': 'integer'},
    'total_reads': {'required': True, 'type': 'integer'},
    'adapter_removal': {
        'required': True,
        'type': 'dict',
        'schema': {
            'cmd_run': {'type': 'string', 'required': True},
            'ftrimmed_reads': {'type': 'integer', 'required': True, 'min': 0},
            'ktrimmed_reads': {'type': 'integer', 'required': True, 'min': 0},
            'total_removed_reads': {'type': 'integer',
                                    'required': True,
                                    'min': 0},
            'trimmed_by_overlap_reads': {'type': 'integer',
                                         'required': True,
                                         'min': 0}
        }
    },
    'contaminant_removal': {

        'required': True,
        'type': 'dict',
        'schema': {
            'cmd_run': {'type': 'string', 'required': True},
            'contaminants': {'type': 'integer', 'required': True, 'min': 0},
            'total_removed_reads': {'type': 'integer', 'required': True, 'min': 0}
        }
    },
    'quality_trimming': {

        'required': True,
        'type': 'dict',
        'schema': {
            'cmd_run': {'type': 'string', 'required': True},
            'total_removed_reads': {'type': 'integer', 'required': True, 'min': 0}
        }
    },
}

'''
NONPAREIL
'''

nonpareil = {
    'c': {'type': 'decimal'},
    'diversity': {'required': True, 'type': 'decimal'},
    'input': {'required': True, 'type': 'string', 'regex': '^s3:\/\/.+'},
    'kappa': {'required': True, 'type': 'decimal'},
    'lr': {'required': True, 'type': 'decimal'},
    'lr_star': {'required': True, 'type': 'decimal'},
    'modelr': {'required': True, 'type': 'decimal'},
    'output': {'required': True, 'type': 'string', 'regex': '^s3:\/\/.+'},
    'pdf': {'required': True, 'type': 'string', 'regex': '^s3:\/\/.+'},
    'tsv': {'required': True, 'type': 'string', 'regex': '^s3:\/\/.+'}
}

'''
SEQUENCINGINFO
'''

sequencing_info = {
    "avg_length": {'type': 'integer', 'min': 0},
    "bases": {'type': 'integer', 'required': True, 'min': 0},
    "insert_size": {'type': ['integer', 'nonestring'], 'min': 0},
    "library_layout": {'type': 'string', 'allowed': ['PAIRED', 'UNPAIRED'],
                       'required': True},
    "library_selection": {'type': 'string', 'allowed': ['RANDOM'],
                          'required': True},
    "library_source": {'type': 'string',
                       'allowed': ['METAGENOMIC', 'METATRANSCRIPTOMIC'],
                       'required': True},
    "library_strategy": {'type': 'string', 'allowed': ['WGS'], 'required': True},
    "model": {'type': 'string', 'required': True},
    "platform": {'type': 'string', 'required': True},
    "raw_read_paths": {'type': 'dict', 'required': True, 'schema': {
        "fwd": {"type": "string", "required": True, "regex": '^s3:\/\/.+'},
        "rev": {"type": "string", "required": True, "regex": '^s3:\/\/.+'},
        }
    },
    "sample_name": {"type": "string", "required": True},
    "size_mb": {"type": "dict", "required": True, "schema": {
      "fwd": {"type": "decimal", "required": True},
      "rev": {"type": "decimal", "required": True},
      }
    },
    "spots": {'type': ['integer', 'nonestring'], "required": True},
    "spots_with_mates": {'type': ['integer', 'nonestring'], "required": True},
    "cmd_run": {'type': 'nonestring', "required": True}
}

'''
MAPPING
'''

mapping = {
    'aligned_mapq_greaterequal_10': {'required': True, 'type': 'integer'},
    'aligned_mapq_less_10': {'required': True, 'type': 'integer'},
    'percent_pairs': {'required': True, 'type': 'decimal'},
    'reads_per_sec': {'required': True, 'type': 'integer'},
    'seed_size': {'required': True, 'type': 'integer'},
    'time_in_aligner_seconds': {'required': True, 'type': 'integer'},
    'too_short_or_too_many_NNs': { 'required': True, 'type': 'integer'},
    'total_bases': {'required': True, 'type': 'integer'},
    'total_reads': {'required': True, 'type': 'integer'},
    'unaligned': {'required': True, 'type': 'integer'},
    'reads_mapped': {
        'required': True, 'type': 'dict', 'schema': {
            'fwd': {'required': True, 'type': 's3path'},
            'rev': {'required': True, 'type': 's3path'}
        }
    },
    'reference': {'required': True, 'type': 'string'}
}

megahit = {
    'sequence_parameters': {'required': True, 'type': 'dict', 'schema': {
        "length": {'required': True, 'type': 'list', 'schema': {
            'type': 'integer'}},
        "gc": {'required': True, 'type': 'list', 'schema': {
            'type': 'decimal'}},
        "description": {'required': True, 'type': 'list', 'schema': {
            'type': 'string'}},
        "sequence": {'required': True, 'type': 'list', 'schema': {
            'type': 'string'}},
        "non_ns": {'required': True, 'type': 'list', 'schema': {
            'type': 'integer'}},
        "seq_num": {'required': True, 'type': 'list', 'schema': {
            'type': 'integer'}}}},
    "length_distribution": {'required': True, 'type': 'dict', 'schema': {
        "num_sequences": {'required': True, 'type': 'list', 'schema': {
            'type': 'integer'}},
        "num_sequences_percent": {'required': True, 'type': 'list', 'schema': {
            'type': 'decimal'}},
        "num_bps": {'required': True, 'type': 'list', 'schema': {
            'type': 'integer'}},
        "num_bps_percent": {'required': True, 'type': 'list', 'schema': {
            'type': 'decimal'}},
        "start": {'required': True, 'type': 'list', 'schema': {
            'type': 'integer'}},
        "end": {'required': True, 'type': 'list', 'schema': {
            'type': 'integer'}}}},
    'total_seqs': {'required': True, 'type': 'integer'},
    'total_bps': {'required': True, 'type': 'integer'},
    'n50': {'required': True, 'type': 'integer'},
    'avg_seq_len': {'required': True, 'type': 'decimal'}
    }


jgi_metadata = {
    "project_name": {'required': True, 'type': 'string'},
    "principle_investigator": {'required': True, 'type': 'string'},
    "scientific_program": {'required': True, 'type': 'string'},
    "product_name": {'required': True, 'type': 'string'},
    "status": {'required': True, 'type': 'string'},
    "status_date": {'required': True, 'type': 'string'},
    "user_program": {'required': True, 'type': 'string'},
    "proposal": {'required': True, 'type': 'string'},
    "jgi_project_id": {'required': True, 'type': 'string'},
    "taxonomy_id": {'required': True, 'type': 'string'},
    "ncbi_project_id": {'required': True, 'type': 'string'},
    "genbank": {'required': True, 'type': 'string'},
    "ena": {'required': True, 'type': 'string'},
    "sra": {'required': True, 'type': 'string'},
    "sequencing_project_id": {'required': True, 'type': 'string'},
    "analysis_project_id": {'required': True, 'type': 'string'},
    "project_manager": {'required': True, 'type': 'string'},
    "portal_id": {'required': True, 'type': 'string'},
    "img_portal": {'required': True, 'type': 'string'}
    }
>>>>>>> cleandata
