#!/usr/bin/env python

from j5test import Utils
import os
import sys

# some helper code for the tests

class SubvalueError(ValueError):
    pass

def sample_method(option):
    if option == 1:
        return "pigeons"
    elif option == 2:
        raise ValueError("Wrong value")
    elif option == 3:
        raise SubvalueError("Wrong subvalue")
    elif option == 4:
        raise KeyError("Wrong key")

@Utils.method_raises(ValueError)
def sample_decorated_function(option):
    if option == 1:
        return "pigeons"
    elif option == 2:
        raise ValueError("Wrong value")
    elif option == 3:
        raise SubvalueError("Wrong subvalue")
    elif option == 4:
        raise KeyError("Wrong key")

@Utils.method_not_raises(KeyError)
def sample_decorated_function_2(option):
    if option == 1:
        return "pigeons"
    elif option == 4:
        raise KeyError("Wrong key")

# here are the actual tests

def test_secure_tmp_file():
    file, file_name = Utils.secure_tmp_file()
    try:
        assert os.path.exists(file_name)
        file.write("Contents".encode('utf-8'))
        file.close()
        assert os.path.exists(file_name)
        reader = open(file_name, "r")
        assert reader.read() == "Contents"
        reader.close()
    finally:
        os.remove(file_name)
        assert not os.path.exists(file_name)

def test_simple_raises_correct():
    """check raising the correct error, and a subclass of the correct error"""
    assert Utils.raises(ValueError, sample_method, 2)
    assert Utils.raises(ValueError, sample_method, 3)

def test_simple_raises_returns():
    """check returning a value causes an error in raises"""
    raised = None
    returned = None
    try:
        returned = Utils.raises(ValueError, sample_method, 1)
    except AssertionError as e:
        raised = e
    except Exception as e:
        raised = e
    assert returned is None
    assert isinstance(raised, AssertionError)
    assert "Call to sample_method did not raise ValueError but returned 'pigeons'" == str(raised)

def test_simple_not_raises_returns():
    """check returning a value doesn't cause an error in not_raises"""
    assert Utils.not_raises(ValueError, sample_method, 1)

def test_simple_raises_incorrect():
    """checks that raises handles an incorrect exception properly"""
    raised = None
    returned = None
    try:
        returned = Utils.raises(ValueError, sample_method, 4)
    except AssertionError as e:
        raised = e
    except Exception as e:
        raised = e
    assert returned is None
    assert isinstance(raised, AssertionError)
    print(str(raised))
    assert "Call to sample_method did not raise ValueError but raised KeyError: 'Wrong key'" == str(raised)

def test_method_raises_correct():
    """check method_raises works with raising the correct error, and a subclass of the correct error"""
    assert sample_decorated_function(2)
    assert sample_decorated_function(3)

def test_method_not_raises_correct():
    """check method_not_raises works with returning a value"""
    assert sample_decorated_function_2(1) == "pigeons"

def test_method_raises_returns():
    """check returning a value causes an error in method_raises"""
    raised = None
    returned = None
    try:
        returned = sample_decorated_function(1)
    except AssertionError as e:
        raised = e
    except Exception as e:
        raised = e
    assert returned is None
    assert isinstance(raised, AssertionError)
    assert "Call to sample_decorated_function did not raise ValueError but returned 'pigeons'" == str(raised)

def test_method_raises_incorrect():
    """checks that method_raises handles an incorrect exception properly"""
    raised = None
    returned = None
    try:
        returned = sample_decorated_function(4)
    except AssertionError as e:
        raised = e
    except Exception as e:
        raised = e
    assert returned is None
    assert isinstance(raised, AssertionError)
    print(str(raised))
    assert "Call to sample_decorated_function did not raise ValueError but raised KeyError: 'Wrong key'" == str(raised)

def test_method_not_raises_incorrect():
    """check method_not_raises works with returning a value"""
    raised = None
    returned = None
    try:
        returned = sample_decorated_function_2(4)
    except AssertionError as e:
        raised = e
    except Exception as e:
        raised = e
    assert returned is None
    assert isinstance(raised, AssertionError)
    print(str(raised))
    assert "Call to sample_decorated_function_2 raised KeyError: 'Wrong key'" == str(raised)

def test_skiptest():
    """checks that this method will be skipped"""
    assert True
    Utils.skip("This method should be skipped, as it is testing skipping methods")
    raise AssertionError("This test should have been skipped")

@Utils.method_raises(Utils.Skipped)
def test_catchskip():
    """Tests that a properly decorated method is skipped - this must be run..."""
    assert True
    Utils.skip("This method should be skipped, as it is testing skipping methods")
    raise AssertionError("This test should have been skipped")

def find_extraterrestrial_beavers():
    """returns whether we can find any extraterrestrial beavers"""
    return False

def find_terrestrial_beavers():
    """returns whether we can find any terrestrial beavers"""
    return True

class ContradictionInTerms(Exception):
    pass

def find_terrestrial_aliens():
    """returns whether we can find any terrestrial aliens"""
    raise ContradictionInTerms("Terrestrial aliens is an oxymoron")

@Utils.method_raises(Utils.Skipped)
@Utils.if_check(find_extraterrestrial_beavers, "check for extraterrestrial beavers")
def test_conditional_check_fails():
    """Tests that this test is not run"""
    raise AssertionError("This test should have been skipped with a message about the missing extraterrestrial beavers""")

@Utils.method_not_raises(Utils.Skipped)
@Utils.if_check(find_terrestrial_beavers, "check for terrestrial beavers")
def test_conditional_check_passes():
    """Tests that this test is run"""
    assert True

@Utils.method_raises(ContradictionInTerms)
@Utils.if_check(find_terrestrial_aliens, "check for terrestrial aliens")
def test_conditional_check_error_propagates():
    """Tests that this test is run"""
    raise AssertionError("This test should have raise a ContradictionInTerms in the check for terrestrial aliens")

@Utils.method_raises(Utils.Skipped)
@Utils.if_module(None, "Badgers")
def test_conditional_module_missing():
    """Tests that this test is not run..."""
    raise AssertionError("This test should have been skipped with a message about the Badgers module""")

@Utils.method_not_raises(Utils.Skipped)
@Utils.if_module(Utils, "j5test.Utils")
def test_conditional_module_present():
    """Tests that this test is run..."""
    assert True


@Utils.method_raises(Utils.Skipped)
@Utils.if_platform("Badgers")
def test_conditional_platform_missing():
    """Tests that this test is not run..."""
    raise AssertionError("This test should have been skipped with a message about the platform""")

@Utils.method_not_raises(Utils.Skipped)
@Utils.if_platform("a", "few", sys.platform)
def test_conditional_platform_present():
    """Tests that this test is not skipped..."""
    assert True

@Utils.method_raises(Utils.Skipped)
@Utils.if_executable("ronald-the-uncommon-executable")
def test_conditional_executable_missing():
    """Tests that this test is not skipped"""
    raise AssertionError("This test should have been skipped with a message about the missing executable""")

@Utils.method_not_raises(Utils.Skipped)
@Utils.if_executable(sys.executable)
def test_conditional_executable_present():
    """Tests that this test is not skipped"""
    assert True

def test_expect_external_error_for():
    """Checks that expected errors are skipped when the right options are passed"""
    wrapper = Utils.expect_external_error_for(KeyError, "Key errors for 4", Utils.contains_expected_kwargs(option=4))(sample_method)
    # check that when passing through the expected option the correct error is raised
    assert Utils.method_raises(Utils.ExpectedExternalError)(wrapper)(4)
    assert Utils.method_raises(Utils.ExpectedExternalError)(wrapper)(option=4)
    # check that when passing in different options an exception comes through normally
    assert Utils.method_raises(ValueError)(wrapper)(option=3)
    # check that when passing in different options a return value comes through normally
    assert wrapper(1) == "pigeons"
    assert wrapper(option=1) == "pigeons"
    # check that an assertion is raised if the expected error is not raised
    wrapper = Utils.expect_external_error_for(KeyError, "Key errors for 4", Utils.contains_expected_kwargs(option=3))(sample_method)
    assert Utils.method_raises(AssertionError)(wrapper)(option=3)
    wrapper = Utils.expect_external_error_for(KeyError, "Key errors for 4", Utils.contains_expected_kwargs(option=1))(sample_method)
    assert Utils.method_raises(AssertionError)(wrapper)(option=1)

@Utils.method_not_raises(Utils.Skipped)
def test_skip_test_for():
    """Skips the test when the right options are passed"""
    badgers = {"william": "holland", "eric": "new zealand", "cecily": "paraguay"}
    @Utils.skip_test_for("There is no badger", Utils.contains_expected_kwargs(badger="scott"))
    def find_badger(badger):
        """tries to find the given badger"""
        return badgers[badger]
    assert Utils.method_raises(Utils.Skipped)(find_badger)("scott")
    assert find_badger("william") == "holland"

def check_that_passes():
    """A check that we know always passes"""
    assert True

def check_that_fails_assert():
    """A check that we know always fails with an AssertionError"""
    assert False

def check_that_raises_error():
    """A check that we know always fails with a ValueError"""
    raise ValueError("This is wrong")

@Utils.method_not_raises(Utils.Skipped)
@Utils.if_passes(check_that_passes)
def test_if_passes_with_pass():
    assert True

@Utils.method_raises(Utils.Skipped)
@Utils.if_passes(check_that_fails_assert)
def test_if_passes_with_assert():
    raise AssertionError("This should be skipped")

@Utils.method_raises(Utils.Skipped)
@Utils.if_passes(check_that_raises_error)
def test_if_passes_with_error():
    raise AssertionError("This should be skipped")

@Utils.method_raises(Utils.Skipped)
@Utils.if_passes(check_that_passes, check_that_fails_assert)
def test_if_passes_with_multiple():
    raise AssertionError("This should be skipped")

def test_skipped_printable():
    """Tests that skipped objects are printable"""
    error = Utils.Skipped("The Message")
    assert "The Message" in str(error)

