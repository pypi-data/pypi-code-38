import os
import glob
import subprocess
import sys

try:
    from bsub import bsub
    from bsub.bsub import BSubJobNotFound

    bsub_avail = True
except ImportError:
    bsub_avail = False

from lib5c.util.system import shell_quote


def infer_replicate_names(infiles, as_dict=False, pattern=None):
    """
    Infers replicate names given a list of filenames.

    Parameters
    ----------
    infiles : list of str
        The filenames to consider.
    as_dict : bool
        Pass True to make this function return a dict mapping the the infiles to
        their inferred replicate names.
    pattern : str, optional
        If the infiles are glob-based matches to a patten containing one
        wildcard, pass that pattern to use it to reconstruct the replicate
        names.

    Returns
    -------
    list of str or dict
        If as_dict is False (the default), this is just the list of inferred rep
        names, in the same order as infiles. If as_dict is True, this is a dict
        mapping the original infiles to their inferred replicate names.
    """
    if pattern:
        prefix, postfix = pattern.split('*')
        if as_dict:
            return {infile: infile[len(prefix):-len(postfix)]
                    for infile in infiles}
        return [infile[len(prefix):-len(postfix)] for infile in infiles]
    common_prefix = os.path.commonprefix(infiles)
    common_postfix = os.path.commonprefix(
        [infile[::-1] for infile in infiles])[::-1]
    if len(infiles) == 1:
        common_prefix = ''
        common_postfix = ''
    if as_dict:
        return {
            infile: infile[len(common_prefix):len(infile)-len(common_postfix)]
            for infile in infiles
        }
    return [infile[len(common_prefix):len(infile)-len(common_postfix)]
            for infile in infiles]


def infer_level_mapping(rep_names, triggers):
    """
    Infers a mapping from replicate names to level names (i.e., classes or
    conditions) using a simple trigger substring approach.

    A replicate is assigned to a level if the level's trigger substring is a
    substring of the replicate name.

    Parameters
    ----------
    rep_names : list of str
        The replicate names to assign levels to.
    triggers : dict or list of str
        Pass a dict mapping trigger substrings to level names, or pass a list of
        level names to use the level names as their own trigger substrings.

    Returns
    -------
    dict
        A mapping from rep_names to level names.
    """
    # resolve triggers
    if type(triggers) is not dict:
        triggers = {trigger: trigger for trigger in triggers}

    levels = {}
    for rep_name in rep_names:
        target_level = None
        for t in triggers:
            if t in rep_name:
                target_level = triggers[t]
                print('assigning rep %s to class %s' % (rep_name, target_level))
                break
        if target_level is None:
            raise ValueError('could not assign replicate %s to any of the '
                             'color-coding classes %s'
                             % (rep_name, triggers.values()))
        else:
            levels[rep_name] = target_level

    return levels


def _determine_flags(parser, args):
    args_dict = vars(args)
    args_string = ''
    for action in parser._actions:
        if action.dest == 'help' or r'%s' in args_dict[action.dest]:
            continue
        if len(action.option_strings) > 0:
            args_string += ' --%s %s' % (action.dest, args_dict[action.dest])
    return args_string


def _parallelize_flags(parser, args, subcommand='', key_arg='infile'):
    # turn args into a dict
    args_dict = vars(args)

    # glob for infiles
    infiles = glob.glob(args_dict[key_arg])

    # infer replicate names
    replicate_names = infer_replicate_names(
        infiles, pattern=args_dict[key_arg]
        if '*' in args_dict[key_arg] else None)

    # construct the args_strings
    args_strings = []
    for i in range(len(infiles)):
        rep = replicate_names[i]
        infile = infiles[i]
        args_string = ''
        for action in parser._actions:
            # print action.dest
            # skip help flag
            if action.dest in ['help', 'version']:
                continue

            # recurse into subparsers
            if action.dest == '==SUPPRESS==':
                # print 'recursing into'
                # print action
                if not subcommand:
                    subcommand = action.choices.keys()[0]
                if ' ' in subcommand:
                    subcommand, subsubcommand = subcommand.split(' ', 1)
                    return _parallelize_flags(action.choices[subcommand], args,
                                              subcommand=subsubcommand,
                                              key_arg=key_arg)
                return _parallelize_flags(action.choices[subcommand], args,
                                          key_arg=key_arg)

            # optional arguments
            if len(action.option_strings) > 0:
                # skip if the value is None
                if args_dict[action.dest] is None:
                    continue
                # special logic for booleans, assumed to use store_true
                elif type(args_dict[action.dest]) == bool:
                    if args_dict[action.dest]:
                        args_string += ' --%s' % action.dest
                # standard optional arguments
                else:
                    opt_value = args_dict[action.dest]
                    if type(opt_value) == str:
                        if r'%s' in args_dict[action.dest]:
                            opt_value = opt_value.replace(r'%s', rep)
                    args_string += ' --%s %s' % \
                                   (action.dest, shell_quote(opt_value))

            # positional arguments
            else:
                if action.dest == key_arg:
                    args_string += ' %s' % infile
                else:
                    pos_value = args_dict[action.dest]
                    if type(pos_value) == str:
                        if r'%s' in args_dict[action.dest]:
                            pos_value = pos_value.replace(r'%s', rep)
                    args_string += ' %s' % shell_quote(pos_value)
        args_strings.append(args_string)
    return args_strings


def resolve_parallel(parser, args, subcommand='', key_arg='infile',
                     root_command='lib5c'):
    """
    Parallelizes as a command via bsub if it is available.

    Parameters
    ----------
    parser : argparse.ArgumentParser
        The parser used to parse the args for the root command.
    args : argparse.Namespace
        The args parsed by the parser.
    subcommand : str
        The particular subcommand of the root command being invoked.
    key_arg : str
        The argument to parallelize over.
    root_command : str
        The string used to invoke the root command.
    """
    # resolve script name
    script_name = '%s %s' % (root_command, subcommand)

    # turn args into a dict
    args_dict = vars(args)

    # glob for infiles
    infiles = glob.glob(args_dict[key_arg])
    if len(infiles) > 1 or '*' in args_dict[key_arg]:
        args_strings = _parallelize_flags(parser, args, subcommand=subcommand,
                                          key_arg=key_arg)
        if bsub_avail:
            if not os.path.exists('logs'):
                os.makedirs('logs')
            try:
                job_ids = []
                for arg_string in args_strings:
                    sub = bsub(
                        '.'.join([script_name.replace(' ', '.')] +
                                 ['%s_%s' % (k, v)
                                  for k, v in args_dict.iteritems()
                                  if k not in ['func', 'infile', 'outfile',
                                               'hang', 'primerfile']]),
                        verbose=False
                    )
                    command = '%s %s' % (script_name, arg_string)
                    sub(command)
                    job_ids.append(sub.job_id)
                if 'hang' in args_dict and args_dict['hang']:
                    for job_id in job_ids:
                        bsub.poll(job_id)
            except BSubJobNotFound:
                for arg_string in args_strings:
                    command = '%s %s' % (script_name, arg_string)
                    print(command)
                    subprocess.call(command, shell=True)
        else:
            for arg_string in args_strings:
                command = '%s %s' % (script_name, arg_string)
                print(command)
                subprocess.call(command, shell=True)
        sys.exit()


def split_self_regionally(regions, script='lib5c', hang=False):
    """
    Allows a command line script that accepts a --region flag to split itself
    into a separate command run for each region.

    Parameters
    ----------
    regions : list of str
        The regions to split into.
    script : str
        The name of the script to invoke.
    hang : bool
        Pass True to cause the original executing process to hang until all the
        bsub jobs spawned by this function complete. This does nothing if bsub
        is not available.
    """
    if not os.path.exists('logs'):
        os.makedirs('logs')
    n_tokens = len(script.split())
    command_pattern = ' '.join([script] +
                               [arg
                                if arg.startswith('-')
                                else shell_quote(arg)
                                for arg in sys.argv[n_tokens:]] +
                               ['--region %r'])
    if bsub_avail:
        try:
            job_ids = []
            for region in regions:
                sub = bsub('.'.join(sys.argv[1:] + [region]), verbose=False)
                command = command_pattern.replace(r'%r', region)
                print(command)
                sub(command)
                job_ids.append(sub.job_id)
            if hang:
                for job_id in job_ids:
                    bsub.poll(job_id)
        except BSubJobNotFound:
            for region in regions:
                command = command_pattern.replace(r'%r', region)
                print(command)
                subprocess.call(command, shell=True)
    else:
        for region in regions:
            command = command_pattern.replace(r'%r', region)
            print(command)
            subprocess.call(command, shell=True)
    sys.exit()


def resolve_primerfile(infile, primerfile=None):
    """
    Searches for a primerfile next to in infile.

    Parameters
    ----------
    infile : str or list of str
        The infile(s) to look next to.
    primerfile : str, optional
        If you already know where the primerfile is pass it here to skip the
        search.

    Returns
    -------
    str
        The primerfile.
    """
    if primerfile is not None:
        return primerfile

    # glob for infiles
    infiles = []
    if type(infile) == str:
        infiles = glob.glob(infile)
    else:
        for f in infile:
            infiles.extend(glob.glob(f))

    # try to find it
    try:
        return glob.glob(
            os.path.join(os.path.split(infiles[0])[0], '*.bed'))[0]
    except IndexError:
        raise IOError('missing primerfile or countsfile')


def resolve_level(primermap, level='auto'):
    """
    Resolves the level of some input data.

    Parameters
    ----------
    primermap : primermap
        Primermap to try to resolve the level of.
    level : str
        If you already know the level, you can pass it as a string here.

    Returns
    -------
    str
        The resolved level.

    Notes
    -----
    This function operates on a "three in a row" heuristic: if the first three
    bins in the primemap are all of the same size, then we guess that it's bin
    level data.
    """
    if level != 'auto':
        return level
    region = primermap.keys()[0]
    lengths = [primermap[region][i]['end'] - primermap[region][i]['start']
               for i in range(3)]
    if lengths[0] == lengths[1] and lengths[0] == lengths[2]:
        return 'bin'
    else:
        return 'fragment'


def resolve_expected_models(expected_model_string, observed_counts, primermap,
                            level=None):
    """
    Convenience helper for resolving expected models.

    Parameters
    ----------
    expected_model_string : str
        If None, we expect to estimate fresh expected models from
        ``observed_counts``. If a path to a specific countsfile, we expect that
        it contains the expected model to be used for all the observed counts.
        If a glob-expandable path, we expect that each file matching the pattern
        is to be used for one of the observed counts (assuming they too are in
        glob order).
    observed_counts : list of dict of np.ndarray
        Each element in the list is one replicate, represented as a counts dict
        of observed values.
    primermap : primermap
        The primermap to use for parsing files, etc.
    level : {'bin', 'fragment'}
        The level to use if a fresh expected modeul must be estimated.

    Returns
    -------
    list of dict of np.ndarray
        The resolved expected models.
    """
    from lib5c.parsers.counts import load_counts
    from lib5c.algorithms.expected import \
        make_poly_log_log_binned_expected_matrix, \
        make_poly_log_log_fragment_expected_matrix
    if expected_model_string:
        expected_files = glob.glob(expected_model_string)
        if len(expected_files) == len(observed_counts):
            print('loading expected models')
            expected_counts = [load_counts(expected_file, primermap)
                               for expected_file in expected_files]
        elif len(expected_files) == 1:
            print('loading expected model')
            expected_count = load_counts(expected_model_string, primermap)
            expected_counts = [expected_count] * len(observed_counts)
        else:
            raise ValueError('unexpected number of expected countsfiles')
    else:
        print('precomputing expected models')
        if resolve_level(primermap, level) == 'fragment':
            expected_counts = [make_poly_log_log_fragment_expected_matrix(
                observed_count, primermap)
                for observed_count in observed_counts]
        else:
            expected_counts = [make_poly_log_log_binned_expected_matrix(
                observed_count) for observed_count in observed_counts]
    return expected_counts
