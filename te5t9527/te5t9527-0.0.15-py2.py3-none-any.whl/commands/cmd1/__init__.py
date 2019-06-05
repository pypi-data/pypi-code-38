import sys
import argparse

def func(args):
    """detect csv data
    """

    sys.stdout.write('reading data....\n')
    input = args.input

    sys.stdout.write('detecting...\n')
    report = input

    if args.output:
        sys.stdout.write('saving report...\n')
        report.to_csv(args.output)
        sys.stdout.write('report saved!\n')
    else:
        sys.stdout.write(str(report))
        sys.stdout.write('\n')

    return report

ARGS = {
    'info': {
        'name': 'cmd1',
        'description': 'detect data from a csv file',
    },
    'defaults': {
        'func': func,
    },
    'args': [
        {
            'flag': ('-i', '--input'),
            'help': 'the csv file which will be detected',
            'required': True,
        },
        {
            'flag': ('-o', '--output'),
            'help': 'path of the csv report will be saved',
        },
    ]
}
