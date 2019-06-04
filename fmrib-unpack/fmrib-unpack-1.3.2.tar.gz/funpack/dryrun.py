#!/usr/bin/env python
#
# dryrun.py - Dry run
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module contains the :func:`doDryRun` function, which prints
information about what ``funpack`` would do, but doesn't actually do
anything.
"""


import funpack


def doDryRun(dtable, unknowns, unprocessed, dropped, args):
    """Dry run.

    Prints out information about the cleaning/processing that would be applied.

    :arg dtable:      :class:`.DataTable` containing the data
    :arg unknowns:    List of :class:`.Column` objects representing the
                      unknown columns.
    :arg unprocessed: A sequence of :class:`.Column` objects representing
                      columns which are uncategorised, and have no processing
                      or cleaning rules specified on them.
    :arg dropped:     List of :class:`.Column` objects representing the
                      unknown columns.
    :arg args:        :class:`argparse.Namespace` object containing command
                      line arguments
    """

    variables = dtable.variables

    print('funpack {} dry run'.format(funpack.__version__))
    print()
    print('Input data')
    if len(args.infile) > 1 and  args.merge_strategy == 'naive':
        print('  [Using naive merge strategy - column/'
              'variable count may not be accurate!]')

    print('  Loaded columns:                     {}'.format(len(dtable.allColumns)))
    if args.noisy > 0:
        print('\n'.join(['    {}'.format(c.name) for c in dtable.allColumns]))

    print('  Ignored columns:                    {}'.format(len(dropped)))
    if args.noisy > 0:
        print('\n'.join(['    {}'.format(c.name) for c in dropped]))

    print('  Unknown columns:                    {}'.format(len(unknowns)))
    if args.noisy > 0:
        print('\n'.join(['    {}'.format(c.name) for c in unknowns]))

    print('  Unprocessed/uncategorised columns:  {}'.format(len(unprocessed)))
    if args.noisy > 0:
        print('\n'.join(['    {}'.format(c.name) for c in unprocessed]))

    print('  Loaded variables:                   {}'.format(len(variables)))
    if args.noisy > 0:
        print('\n'.join(['    {}'.format(v) for v in variables]))
    print()

    print('Cleaning')

    print()
    print('  NA Insertion: {}'.format(not args.skip_insertna))
    if not args.skip_insertna:
        navals = dtable.vartable['NAValues'].dropna().filter(variables)
        if len(navals) == 0:
            print('    No NA value replacements')
        for vid in sorted(navals.index):
            print('    {}: {}'.format(vid, navals[vid]))

    print()
    print('  Cleaning functions: {}'.format(not args.skip_clean_funcs))
    if not args.skip_clean_funcs:
        cleanfuncs = dtable.vartable['Clean'].dropna().filter(variables)
        if len(cleanfuncs) == 0:
            print('    No cleaning functions')
        for vid in sorted(cleanfuncs.index):
            vcfs = ', '.join([str(f) for f in cleanfuncs[vid].values()])
            print('    {}: [{}]'.format(vid, vcfs))

    print()
    print('  Child value replacement: {}'.format(not args.skip_childvalues))
    if not args.skip_childvalues:
        parentvals = dtable.vartable['ParentValues'].dropna().filter(variables)
        childvals  = dtable.vartable['ChildValues'] .dropna().filter(variables)
        if len(parentvals) == 0:
            print('    No replacements')
        for vid in sorted(parentvals.index):
            print('    {}: [{}] -> {}'.format(
                vid,
                ', '.join(map(str, parentvals[vid])),
                childvals[ vid]))

    print('  Categorical recoding: {}'.format(not args.skip_recoding))
    if not args.skip_recoding:
        rawlevels = dtable.vartable['RawLevels'].dropna().filter(variables)
        newlevels = dtable.vartable['NewLevels'].dropna().filter(variables)
        if len(rawlevels) == 0:
            print('    No recodings')
        for vid in sorted(rawlevels.index):
            print('    {}: {} -> {}'.format(vid,
                                            rawlevels[vid],
                                            newlevels[vid]))

    print()
    print('Processing: {}'.format(not args.skip_processing))
    if not args.skip_processing:
        if len(dtable.proctable) == 0:
            print('No processes')
        for idx in sorted(dtable.proctable.index):
            vids = dtable.proctable.loc[idx, 'Variable']
            vps  = dtable.proctable.loc[idx, 'Process']
            vps  = ', '.join([str(p) for p in vps.values()])

            print('  {}: {} -> [{}]'.format(idx + 1, vids, vps))
