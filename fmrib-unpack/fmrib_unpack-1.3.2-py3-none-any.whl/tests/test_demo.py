#!/usr/bin/env python
#
# test_demo.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#


import time
import json
import glob
import shutil
import sys
import os
import os.path as op
import itertools as it
import subprocess as sp
import multiprocessing as mp

from unittest import mock

import jinja2 as j2
import numpy as np

import notebook.notebookapp as notebookapp
import funpack.scripts.demo as ukbdemo


from . import tempdir


def test_demo():

    def shutdown():
        time.sleep(3)
        for server in notebookapp.list_running_servers():
            notebookapp.shutdown_server(server)

    mp.Process(target=shutdown).start()

    # add some extra args for running within docker
    if op.exists('/.dockerenv'): args = ['--allow-root', '--ip=0.0.0.0']
    else:                        args = None

    with mock.patch('sys.argv', ['funpack_demo']):
        ukbdemo.main(args)


def test_demo_commands():

    def eval_cmd(cmd, out):

        # TODO extract all funpack calls, and turn
        #      them into funpack.main function calls.
        result = sp.run(['bash', cmd], stdout=sp.PIPE)

        with open(out, 'rt') as f:
            out = f.read()
        assert result.returncode              == 0
        assert result.stdout.decode().strip() == out.strip()

    with tempdir() as td:
        td = op.realpath(td)
        gen_demo_tests(rundir=td)
        demodir = op.join(op.dirname(__file__), '..', 'scripts', 'demo')

        for fname in glob.glob(op.join(demodir, '*.*')):
            shutil.copy(fname, td)

        commands = list(sorted(glob.glob('*_command.txt')))
        outputs  = list(sorted(glob.glob('*_output.txt')))

        for i, (cmd, out) in enumerate(zip(commands, outputs)):

            print('Command', i)
            print(open(cmd).read())
            print()

            eval_cmd(cmd, out)


def gen_demo_tests(outdir=None, rundir=None):

    if outdir is None: outdir = os.getcwd()
    if rundir is None: rundir = os.getcwd()

    demofile = op.join(op.dirname(__file__),
                       'funpack_demonstration_with_outputs.ipynb')
    with open(demofile, 'rt') as f:
        content = f.read()

    content = j2.Template(content)
    content = content.render(dir_prefix=rundir, op=op)
    nb      = json.loads(content)
    cells   = nb['cells']

    fname_prefix_format = '{{:0{}d}}'.format(
        int(np.ceil(np.log10(len(cells)))))

    i = 1
    for cell in cells:

        if cell['cell_type'] != 'code':
            continue

        source = cell['source']
        output = cell['outputs']

        # exclude some specific commands
        excludes = ['pygmentize',
                    'ls -l $ukbdir/configs/fmrib']

        if any([exc in line
                for exc, line
                in it.product(excludes, source)]):
            continue

        alloutput = []
        for o in output:
            if o['name'] == 'stdout':
                alloutput += o['text']
        output = alloutput

        cmd_file = '{}_command.txt'.format(
            fname_prefix_format.format(i))
        out_file = '{}_output.txt'.format(
            fname_prefix_format.format(i))

        # Todo abs paths in unknown var file output

        with open(op.join(outdir, cmd_file), 'wt') as f:
            f.write('#!/usr/bin/env bash\n')
            f.write('export PYTHONPATH="{}"\n'.format(
                op.join(op.dirname(__file__), '..', '..')))
            for line in source:
                if line.startswith('funpack'):
                    line = '{} -m '.format(sys.executable) + line
                f.write(line)
        with open(op.join(outdir, out_file), 'wt') as f:
            for line in output:
                f.write(line)

        i += 1
