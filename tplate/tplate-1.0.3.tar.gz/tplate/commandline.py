import argparse
import importlib.util
import jinja2
import json
import os.path
import shutil
import sys
import yaml

TPLATE_SUFFIX = '.tplate'

# files in this list are allowed in the output directory.
ALLOW_IN_OUTDIR_LIST = ['.DS_Store']
NOCOPY_LIST = ['tplate_finalize.py', 'tplate.yaml', 'tplate.json', '.git']


def run():
    """
    The first parameter to this program must specify a template directory and the second must specify an output
    directory.

    All of the contents of the template directory are copied into the output directory.  If there are files in template
    directory that that end with a .tplate extension, they will be processed as jinja2 templates.  The output will be
    placed in the corresponding location under the output directory in a file with the same name, minus the .tplate
    suffix.  For example, to create a templated README.md in the output directory, place a jinja2 template called
    README.md.tplate in the template directory.  There are a couple of exceptions to this.  If a .git folder exists
    it will not be copied. Also, the file tplate.json will not be copied (see below).

    The template directory must contain a file named tplate.json or tplate.yaml, which contains all of the variables
    that are referenced in the template. This purpose of this file is to document the variables that are in the
    templates and to provide default valued.  It should be copied into the output directory and modified.

    The output directory must exist and contain a tplate.json file (or tplate.yaml).  In order to avoid accidentally
    overwriting existing files, tplate will not do anything if there are other files in the output directory.  This
    can be overridden by passing the --update flag
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('template_dir')
    parser.add_argument('output_dir')
    parser.add_argument('--update', action='store_true')

    args = parser.parse_args(sys.argv[1:])
    if not os.path.isdir(args.template_dir):
        sys.exit('The program has exited because the provided template directory ({0}) does not exist.'
                 .format(args.template_dir))

    if not os.path.isdir(args.output_dir):
        sys.exit('The program has exited because the provided output directory ({0}) does not exist.'
                 .format(args.output_dir))

    files = os.listdir(args.output_dir)
    files = [f for f in files if f not in ALLOW_IN_OUTDIR_LIST]
    if not args.update:
        if len(files) != 1 or (files[0] != 'tplate.json' and files[0] != 'tplate.yaml'):
            sys.exit('The output directory ({0}) must contain "tplate.json" or "tplate.yaml" and no other files or '
                     'directories.'.format(args.output_dir))

    configfile = None
    if 'tplate.json' in files:
        with open(os.path.join(args.output_dir, 'tplate.json'), 'r') as envfile:
            environment = json.load(envfile)
    elif 'tplate.yaml' in files:
        with open(os.path.join(args.output_dir, 'tplate.yaml'), 'r') as envfile:
            environment = yaml.safe_load(envfile)
    else:
        sys.exit('The output directory must contain a file named "tplate.json" or "tplate.yaml"')

    # add the output path and template path to the environment
    environment['output_dir'] = args.output_dir
    environment['template_dir'] = args.template_dir

    copydir(args.template_dir, args.output_dir, environment)

    finalize_script = os.path.join(args.template_dir, 'tplate_finalize.py')
    if os.path.isfile(finalize_script):
        spec = importlib.util.spec_from_file_location('tplate.finalize', location=finalize_script)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.run(environment)


def copydir(fromdir, todir, environment):
    template_env = jinja2.Environment(loader=jinja2.FileSystemLoader(fromdir), trim_blocks=True, lstrip_blocks=True)
    for f in os.listdir(fromdir):
        if f in NOCOPY_LIST:
            continue

        infile = os.path.join(fromdir, f)
        if os.path.isdir(infile):
            to = os.path.join(todir, f)
            os.mkdir(to)
            copydir(infile, to, environment)
        else:
            if f.endswith(TPLATE_SUFFIX):
                template = template_env.get_template(f)
                outfile = os.path.join(todir, f[0:-1 * len(TPLATE_SUFFIX)])
                with open(outfile, 'wt') as fp:
                    template.stream(environment).dump(fp)

            else:
                outfile = os.path.join(todir, f)
                shutil.copyfile(infile, outfile)
