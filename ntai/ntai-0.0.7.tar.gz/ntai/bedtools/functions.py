import os, sys, uuid
from ..terminal.tools import short_arg, long_arg, flag_arg

def getfasta(
    fi:     str,
    bed:    str = '/dev/stdin',
    fo:     str = '/dev/stdout',
    name:   bool = False,
    tab:    bool = False,
    bedOut: bool = False,
    s:      bool = False,
    split:  bool = False
) -> list:
    '''
    Arguments:
        fi (str): input FASTA

        bed (str): <BED/GFF/VCF>

        fo (str): Specify an output file name. By default, output goes to stdout

        name (bool): Use the “name” column in the BED file for the FASTA headers
            in the output FASTA file.

        tab (bool): Report extract sequences in a tab-delimited format instead
            of in FASTA format.

        bedOut (bool): Report extract sequences in a tab-delimited BED format
            instead of in FASTA format.

        s (bool): Force strandedness. If the feature occupies the antisense
            strand, the sequence will be reverse complemented. Default: strand
            information is ignored.

        split (bool): Given BED12 input, extract and concatenate the sequences
            from the BED “blocks” (e.g., exons)
    Returns:
        command (list): a list of strings containing the bedtools getfasta
            command
    '''
    if name: name = uuid.uuid4()
    if tab: tab = uuid.uuid4()
    if bedOut: bedOut = uuid.uuid4()
    if s: s = uuid.uuid4()
    if split: split = uuid.uuid4()
    _fi = fi
    del fi
    fi = _fi
    command = [
        'bedtools',
        'getfasta',
        *short_arg(fi, 'fi'), *short_arg(bed, 'bed'), *short_arg(fo, 'fo'),
        flag_arg(name, 'name', short=True), flag_arg(tab, 'tab', short=True),
        flag_arg(bedOut, 'bedOut', short=True), flag_arg(s, 's', short=True),
        flag_arg(split, 'split', short=True)
    ]
    return command
