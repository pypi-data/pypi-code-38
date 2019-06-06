###############################################################################
# (c) Copyright 2018 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
__author__ = 'Chris Burr <c.b@cern.ch>'

import distutils.spawn
import os
import sys
from subprocess import check_output, CalledProcessError, STDOUT

from nose import SkipTest
from LbPlatformUtils.inspect import os_id

if os_id().endswith('slc6'):
    CAN_RUN_NATIVE_SLC5 = True
    CAN_RUN_NATIVE_SLC6 = True
    CAN_RUN_NATIVE_CENTOS7 = False
elif os_id().endswith('centos7'):
    CAN_RUN_NATIVE_SLC5 = False
    CAN_RUN_NATIVE_SLC6 = True
    CAN_RUN_NATIVE_CENTOS7 = True
else:
    CAN_RUN_NATIVE_SLC5 = False
    CAN_RUN_NATIVE_SLC6 = False
    CAN_RUN_NATIVE_CENTOS7 = False


BASE_LBRUN_COMMAND = ['lb-run', '--debug', '--siteroot', '/cvmfs/lhcb.cern.ch/lib']


def _check_gaudirun(options):
    output = check_output(BASE_LBRUN_COMMAND + options + ['gaudirun.py'],
                          stderr=STDOUT)
    output = output.decode()
    assert 'Application Manager Terminated successfully' in output
    used_container = 'preparing singularity wrapper command' in output
    return output, used_container


def setup():
    if not os.path.isdir('/cvmfs/lhcb.cern.ch'):
        raise SkipTest("Skipping integration tests due to missing siteroot")
    if not os.path.isdir('/cvmfs/cernvm-prod.cern.ch'):
        raise SkipTest("Skipping integration tests due to missing cernvm")
    if not distutils.spawn.find_executable('singularity'):
        raise SkipTest("Skipping integration tests due to missing singularity")

    from os.path import join, dirname, pardir, abspath
    # FIXME compatibility py2-py3
    if sys.version_info >= (3, ):
        os.environ['CMAKE_PREFIX_PATH'] = abspath(
            join(
                dirname(__file__), pardir, pardir, pardir, pardir, pardir,
                'python', 'LbEnv', 'ProjectEnv', 'tests', 'data'))
    else:
        os.environ['CMAKE_PREFIX_PATH'] = join(dirname(__file__), 'data')


def test_setupproject():
    command = ['--platform', 'x86_64-slc5-gcc46-opt', 'Gaudi/v23r0']
    try:
        output, used_container = _check_gaudirun(command)
    except CalledProcessError:
        assert not CAN_RUN_NATIVE_SLC5, output
    else:
        assert CAN_RUN_NATIVE_SLC5, output

    output, used_container = _check_gaudirun(['--container', 'singularity'] + command)
    assert used_container, output

    output, used_container = _check_gaudirun(['--allow-containers'] + command)
    assert used_container != CAN_RUN_NATIVE_SLC5, output
    if not CAN_RUN_NATIVE_SLC5:
        assert 'Decided best container to use is' in output, output

    output, used_container = _check_gaudirun(['--allow-containers', '--prefer-container'] + command)
    assert used_container, output
    assert 'Decided best container to use is' in output, output


def test_setupproject_best():
    command = ['--platform', 'best', 'Gaudi/v23r0']
    try:
        output, used_container = _check_gaudirun(command)
    except CalledProcessError:
        assert not CAN_RUN_NATIVE_SLC5, output
    else:
        assert CAN_RUN_NATIVE_SLC5, output
        assert not used_container, output

    output, used_container = _check_gaudirun(['--container', 'singularity'] + command)
    assert used_container, output

    output, used_container = _check_gaudirun(['--allow-containers'] + command)
    assert used_container != CAN_RUN_NATIVE_SLC5, output
    if not CAN_RUN_NATIVE_SLC5:
        assert 'Decided best container to use is' in output, output

    output, used_container = _check_gaudirun(['--allow-containers', '--prefer-container'] + command)
    assert used_container, output
    assert 'Decided best container to use is' in output, output


def test_lbrun_slc6():
    command = ['--platform', 'x86_64-slc6-gcc8-opt', 'Gaudi/v32r0']
    try:
        output, used_container = _check_gaudirun(command)
    except CalledProcessError:
        assert not CAN_RUN_NATIVE_SLC6, output
    else:
        assert CAN_RUN_NATIVE_SLC6, output
        assert not used_container, output

    output, used_container = _check_gaudirun(['--container', 'singularity'] + command)
    assert used_container, output

    output, used_container = _check_gaudirun(['--allow-containers'] + command)
    assert used_container != CAN_RUN_NATIVE_SLC6, output
    if not CAN_RUN_NATIVE_SLC6:
        assert 'Decided best container to use is' in output, output

    output, used_container = _check_gaudirun(['--allow-containers', '--prefer-container'] + command)
    assert used_container, output
    assert 'Decided best container to use is' in output, output


def test_lbrun_centos7():
    command = ['--platform', 'x86_64-centos7-gcc8-opt', 'Gaudi/v32r0']
    try:
        output, used_container = _check_gaudirun(command)
    except CalledProcessError:
        assert not CAN_RUN_NATIVE_CENTOS7, output
    else:
        assert CAN_RUN_NATIVE_CENTOS7, output
        assert not used_container, output

    output, used_container = _check_gaudirun(['--container', 'singularity'] + command)
    assert used_container, output

    output, used_container = _check_gaudirun(['--allow-containers'] + command)
    assert used_container != CAN_RUN_NATIVE_CENTOS7, output
    if not CAN_RUN_NATIVE_CENTOS7:
        assert 'Decided best container to use is' in output, output

    output, used_container = _check_gaudirun(['--allow-containers', '--prefer-container'] + command)
    assert used_container, output
    assert 'Decided best container to use is' in output, output


def test_lbrun_best():
    command = ['--platform', 'best', 'Gaudi/v32r0']
    try:
        output, used_container = _check_gaudirun(command)
    except CalledProcessError:
        assert not (CAN_RUN_NATIVE_SLC6 or CAN_RUN_NATIVE_CENTOS7), output
    else:
        assert (CAN_RUN_NATIVE_SLC6 or CAN_RUN_NATIVE_CENTOS7), output
        assert not used_container, output

    output, used_container = _check_gaudirun(['--container', 'singularity'] + command)
    assert used_container, output

    output, used_container = _check_gaudirun(['--allow-containers'] + command)
    assert used_container != (CAN_RUN_NATIVE_SLC6 or CAN_RUN_NATIVE_CENTOS7), output
    if not (CAN_RUN_NATIVE_SLC6 or CAN_RUN_NATIVE_CENTOS7):
        assert 'Decided best container to use is' in output, output

    output, used_container = _check_gaudirun(['--allow-containers', '--prefer-container'] + command)
    assert used_container, output
    assert 'Decided best container to use is' in output, output
