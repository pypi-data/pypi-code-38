# encoding: utf-8
from __future__ import absolute_import, division, print_function

import sys

IS_WIN = sys.platform == "win32"


def test_fixture(testdir):

    testdir.makepyfile(
        """
        from __future__ import print_function

        import os
        import tempfile
        import time

        import pytest

        here = os.path.abspath(__file__)

        def test_regtest(regtest, tmpdir):

            with regtest:
                print("this is expected outcome")
                print(tmpdir.join("test").strpath)
                print(tempfile.gettempdir())
                print(tempfile.mkdtemp())
                print("obj id is", hex(id(here)))

        def test_always_fail():
            assert 1 * 1 == 2

        def test_always_fail_regtest(regtest):
            regtest.write(str(time.time()))
            assert 1 * 1 == 2

        def test_always_ok():
            assert 1 * 1 == 1

        @pytest.mark.xfail
        def test_xfail_0():
            assert 1 == 2

        @pytest.mark.xfail
        def test_xfail_with_regtest(regtest):
            assert 1 == 2

        def test_always_ok_regtest(regtest):
            regtest.identifier = "my_computer"
            assert 1 * 1 == 1

        @pytest.mark.parametrize("a, b, c", [(1, 2, 3), ("a", "b", "ab")])
        def test_with_paramertrization(a, b, c, regtest):
            print(a, b, c, file=regtest)
            assert a + b == c

    """
    )

    # will fully fail
    result = testdir.runpytest()
    result.assert_outcomes(failed=5, passed=2, xfailed=2)
    result.stdout.fnmatch_lines(
        [
            "regression test output differences for test_fixture.py::test_regtest:",
            "*5 failed, 2 passed, 2 xfailed*",
        ]
    )

    print(result.stdout.str())

    expected_diff = """
                    >   --- current
                    >   +++ tobe
                    >   @@ -1,6 +1 @@
                    >   -THIS IS EXPECTED OUTCOME
                    >   -<TMPDIR_FROM_FIXTURE>/TEST
                    >   -<TMPDIR_FROM_TEMPFILE_MODULE>
                    >   -<TMPDIR_FROM_TEMPFILE_MODULE>
                    >   -OBJ ID IS 0X?????????
                    """.strip().split(
        "\n"
    )

    result.stdout.fnmatch_lines([l.lstrip() for l in expected_diff])
    result.stdout.fnmatch_lines(["*5 failed, 2 passed, 2 xfailed*"])

    # reset
    result = testdir.runpytest("--regtest-reset", "-v")
    result.assert_outcomes(failed=2, passed=5, xfailed=2)
    result.stdout.fnmatch_lines(["*2 failed, 5 passed, 2 xfailed*"])

    # check recorded output
    output_root = testdir.tmpdir.join("_regtest_outputs")

    def _read_output(fname):
        path = output_root.join("test_fixture.{}.out".format(fname))
        return open(path.strpath).read()

    sep = "\\" if IS_WIN else "/"

    assert (
        _read_output("test_regtest")
        == (
            "THIS IS EXPECTED OUTCOME\n"
            "<TMPDIR_FROM_FIXTURE>%sTEST\n"
            "<TMPDIR_FROM_TEMPFILE_MODULE>\n"
            "<TMPDIR_FROM_TEMPFILE_MODULE>\n"
            "OBJ ID IS 0X?????????\n"
        )
        % sep
    )

    reg_test_files = [f.basename for f in output_root.listdir()]
    assert sorted(reg_test_files) == [
        "test_fixture.test_always_ok_regtest__my_computer.out",
        "test_fixture.test_regtest.out",
        "test_fixture.test_with_paramertrization[1-2-3].out",
        "test_fixture.test_with_paramertrization[a-b-ab].out",
    ]

    # check if regtest.identifier = "my_computer" created the output file:
    assert _read_output("test_always_ok_regtest__my_computer") == ""

    # run again, reg test should succeed now
    result = testdir.runpytest()
    result.assert_outcomes(failed=2, passed=5, xfailed=2)
    result.stdout.fnmatch_lines(["*2 failed, 5 passed, 2 xfailed*"])

    # just check if cmd line flags work without throwing exceptions:
    result = testdir.runpytest("--regtest-regard-line-endings")
    result.assert_outcomes(failed=2, passed=5, xfailed=2)

    # just check if cmd line flags work without throwing exceptions:
    result = testdir.runpytest("--regtest-tee")
    result.assert_outcomes(failed=2, passed=5, xfailed=2)
