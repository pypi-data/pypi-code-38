def add_hic_extract_tool(parser):
    hic_extract_parser = parser.add_parser(
        'hic-extract',
        prog='lib5c hic-extract',
        help='extract chunks from Hi-C data'
    )
    hic_extract_parser.add_argument(
        'matrix',
        type=str,
        help='''Path to contact matrix file. %%c will be replaced by the
        chromosome name if multiple files are necessary.''')
    hic_extract_parser.add_argument(
        'range',
        type=str,
        help='''Genomic range to extract, in the form 'chrom:start-end' Pass a
        path to a tab-separated file whose columns are region names and ranges
        to extract multiple named ranges.''')
    hic_extract_parser.add_argument(
        'output_countsfile',
        type=str,
        help='''Path to write extracted counts to.''')
    hic_extract_parser.add_argument(
        'output_bedfile',
        type=str,
        help='''Path to write information about extracted bins to.''')
    hic_extract_parser.add_argument(
        '-b', '--bias_vector_file',
        type=str,
        help='''Path to file containing bias vector that counts will be divided
        by before being written. %%c will be replaced by the chromosome name if
        multiple files are necessary.''')
    hic_extract_parser.set_defaults(func=hic_extract_tool)


def parse_range_string(range_string):
    chrom, start_end = range_string.split(':')
    start, end = start_end.split('-')
    return {'chrom': chrom, 'start': int(start), 'end': int(end)}


def hic_extract_tool(parser, args):
    from lib5c.parsers.hic import load_range_from_contact_matrix
    from lib5c.writers.counts import write_counts
    from lib5c.writers.primers import write_primermap

    # resolve ranges
    if ':' in args.range:
        ranges = {'unnamed_region': parse_range_string(args.range)}
    else:
        with open(args.range, 'r') as handle:
            ranges = {}
            for line in handle:
                if line.startswith('#'):
                    continue
                pieces = line.strip().split('\t')
                ranges[pieces[0]] = parse_range_string(pieces[1])

    # resolve matrix
    matrices = {region: args.matrix.replace(r'%c', ranges[region]['chrom'])
                for region in ranges}

    # resolve bias_vectors
    bias_vectors = None
    if args.bias_vector_file is not None:
        bias_vectors = {
            region: args.bias_vector_file.replace('%c', ranges[region]['chrom'])
            for region in ranges
        }

    # resolve region names
    region_names = {region: region for region in ranges}

    # parse
    counts, pixelmap = load_range_from_contact_matrix(
        matrices, ranges, region_name=region_names, norm_file=bias_vectors)

    # write
    write_counts(counts, args.output_countsfile, pixelmap)
    write_primermap(pixelmap, args.output_bedfile)
