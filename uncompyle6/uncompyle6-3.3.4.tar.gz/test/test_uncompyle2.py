#!/usr/bin/env python
# emacs-mode: -*-python-*-
"""
test_uncompyle2 -- uncompyle and verify Python libraries

Usage-Examples:

  test_uncompyle2.py --all		# decompile all tests (suite + libs)
  test_uncompyle2.py --all --verify	# decomyile all tests and verify results
  test_uncompyle2.py --test		# decompile only the testsuite
  test_uncompyle2.py --verify	# decompile and verify python lib 2.7.11

Adding own test-trees:

Step 1) Edit this file and add a new entry to 'test_options', eg.
          test_options['mylib'] = ('/usr/lib/mylib', PYOC, 'mylib')
Step 2: Run the test:
	  test_uncompyle2 --mylib	  # decompile 'mylib'
	  test_uncompyle2 --mylib --verify # decompile verify 'mylib'
"""

from __future__ import print_function

from multiprocessing import Process, Queue, cpu_count
from Queue import Empty
from uncompyle6 import PYTHON3
from uncompyle2 import main, verify
import os, time, shutil
from fnmatch import fnmatch

#----- configure this for your needs

TEST_VERSIONS=('2.7.12', '2.7.13')

target_base = '/tmp/py-dis/'
lib_prefix = os.path.join(os.environ['HOME'], '.pyenv/versions')

PYC = ('*.pyc', )
PYO = ('*.pyo', )
PYOC = ('*.pyc', '*.pyo')

#-----

test_options = {
    # name: (src_basedir, pattern, output_base_suffix)
    'test': ('./test', PYOC, 'test'),
    }

for vers in TEST_VERSIONS:
    if vers.startswith('pypy-'):
        short_vers = vers[0:-2]
        test_options[vers] = (os.path.join(lib_prefix, vers, 'lib_pypy'),
                              PYC, 'python-lib'+short_vers)
    else:
        short_vers = vers[:3]
        test_options[vers] = (os.path.join(lib_prefix, vers, 'lib', 'python'+short_vers),
                              PYC, 'python-lib'+short_vers)

def do_tests(src_dir, patterns, target_dir, start_with=None, do_verify=False):

    def visitor(files, dirname, names):
        files.extend(
            [os.path.normpath(os.path.join(dirname, n))
                 for n in names
                    for pat in patterns
                        if fnmatch(n, pat)])

    files = []
    cwd = os.getcwd()
    os.chdir(src_dir)
    if PYTHON3:
        for root, dirname, names in os.walk(os.curdir):
            files.extend(
                [os.path.normpath(os.path.join(root, n))
                     for n in names
                        for pat in patterns
                            if fnmatch(n, pat)])
            pass
        pass
    else:
        os.path.walk(os.curdir, visitor, files)
    os.chdir(cwd)
    files.sort()

    if start_with:
        try:
            start_with = files.index(start_with)
            files = files[start_with:]
            print('>>> starting with file', files[0])
        except ValueError:
            pass

    if len(files) > 200:
        files = [file for file in files if not 'site-packages' in file]
        files = [file for file in files if not 'test' in file]
        if len(files) > 200:
            files = files[:200]

    print(time.ctime())
    outfile = None
    main.main(src_dir, target_dir, files, [], outfile,
              showasm=False, showast=False, do_verify=do_verify, py=1, deob=0)
    print(time.ctime())

def process_func(fq, rq, src_base, out_base, codes, outfile, showasm, showast, do_verify, py, deob):
    try:
        (tot_files, okay_files, failed_files, verify_failed_files) = (0,0,0,0)
        while 1:
            f = fq.get()
            if f == None:
                break
            (t, o, f, v) = \
                main(src_base, out_base, [f], codes, outfile, showasm, showast, do_verify, py, deob)
            tot_files += t
            okay_files += o
            failed_files += f
            verify_failed_files += v
    except (Empty, KeyboardInterrupt):
        pass
    rq.put((tot_files, okay_files, failed_files, verify_failed_files))
    rq.close()

if __name__ == '__main__':
    import getopt, sys

    codes = []
    do_coverage = do_verify = False
    test_dirs = []
    start_with = None

    test_options_keys = list(test_options.keys())
    test_options_keys.sort()
    opts, files = getopt.getopt(sys.argv[1:], 'hatdrmso:c:',
                                ['help', 'verify', 'showast', 'showasm', 'norecur', 'py',
                                 'deob'] + test_options_keys )
    vers = ''
    for opt, val in opts:
        if opt in ('-h', '--help'):
            print(__doc__)
            sys.exit(0)
        elif opt == '--verify':
            do_verify = 1
        elif opt in ('--showasm', '-a'):
            showasm = 1
            do_verify = 0
        elif opt in ('--showast', '-t'):
            showast = 1
            do_verify = 0
        elif opt == '-o':
            outfile = val
        elif opt == '-d':
            timestamp = False
        elif opt == '-c':
            codes.append(val)
        elif opt == '-m':
            multi = 1
        elif opt == '--norecur':
            norecur = 1
        elif opt == '-s':
            strip_common_path = 1
        elif opt == '--py':
            py = 1
        elif opt == '--deob':
            deob = 1
        if opt == '--verify':
            do_verify = True
        elif opt[2:] in test_options_keys:
            triple = test_options[opt[2:]]
            vers = triple[-1]
            test_dirs.append(triple)
        elif opt == '--all':
            vers = 'all'
            for val in test_options_keys:
                test_dirs.append(test_options[val])

    for src_dir, pattern, target_dir in test_dirs:
        if os.path.exists(src_dir):
            target_dir = os.path.join(target_base, target_dir)
            if os.path.exists(target_dir):
                shutil.rmtree(target_dir, ignore_errors=1)
            do_tests(src_dir, pattern, target_dir, start_with, do_verify)
        else:
            print("### Path %s doesn't exist; skipping" % src_dir)

# python 1.5:

# test/re_tests		memory error
# test/test_b1		memory error

# Verification notes:
# - xdrlib fails verification due the same lambda used twice
#   (verification is successfull when using original .pyo as
#   input)
#
