import ConfigParser
import pytest
import RaveEngine.configManager as configManager
import RaveEngine.projectManager as projectManager
import Utils.commandManager as commandManager
import Utils.sad as sad
from flaky import flaky

@pytest.fixture(autouse=True)
def setup():
    projectManager.createInitProject()
    yield
    commandManager.runRmDirCommand(sad._CONFIG_DIR_NAME_)
    commandManager.runRmDirCommand(sad._LOG_DIR_NAME_)
    commandManager.runRmDirCommand(sad._MODULES_DIR_)

def data_get():
    trueData = [(sad._CONFIG_RAVEGEN_SECTION_, sad._CONFIG_HOSTING_OPTION_, sad._DEPLOY_HEROKU_OPTION)]
    falseData_1 = [(sad._CONFIG_RAVEGEN_SECTION_, "TEST", None)]
    falseData_2 = [("TEST", "TEST", None)]
    return trueData + falseData_1 + falseData_2

def data_getBoolean():
    yesData = [("yes", True), ("YES", True), ("YeS", True)]
    noData = [("no", False), ("NO", False)]
    return yesData + noData

def data_set():
    data = [(sad._CONFIG_RAVEGEN_SECTION_, "TEST", "TEST")]
    data += [(sad._CONFIG_RAVEGEN_SECTION_, sad._CONFIG_HOSTING_OPTION_, "TEST")]
    data += [("SEC-TEST", "TEST-OP", "TEST")]
    return data

def data_setSection():
    trueData = [("TEST-SEC")]
    falseData = [sad._CONFIG_RAVEGEN_SECTION_]
    return trueData + falseData

@flaky(3,1)
def test_getConfig():
    config = configManager.getConfig()
    assert isinstance(config, ConfigParser.RawConfigParser)
    commandManager.runRmCommand(sad._CONFIG_FILE_PATH)
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        config = configManager.getConfig()
    assert pytest_wrapped_e.type == SystemExit
    commandManager.runRmCommand(sad._CONFIG_DIR_NAME_)
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        config = configManager.getConfig()
    assert pytest_wrapped_e.type == SystemExit

@flaky(3,1)
def test_verifyConfig():
    config = configManager.getConfig()
    configManager.verifyConfig(config)
    configManager.set(config, sad._CONFIG_RAVEGEN_SECTION_, sad._CONFIG_HOSTING_OPTION_, "TEST")
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        configManager.verifyConfig(config)
    assert pytest_wrapped_e.type == SystemExit
    configManager.set(config, sad._CONFIG_RAVEGEN_SECTION_, sad._CONFIG_HOSTING_OPTION_, sad._DEPLOY_HEROKU_OPTION)
    configManager.set(config, sad._CONFIG_RAVEGEN_SECTION_, sad._CONFIG_TOKEN_OPTION_, "")
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        configManager.verifyConfig(config)
    assert pytest_wrapped_e.type == SystemExit
    commandManager.runRmCommand(sad._CONFIG_FILE_PATH)
    commandManager.runTouchCommand(sad._CONFIG_FILE_PATH)
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        config = configManager.getConfig()
    assert pytest_wrapped_e.type == SystemExit

@flaky(3,1)
@pytest.mark.parametrize('section, option, expected', data_get())
def test_get(section, option, expected):
    config = configManager.getConfig()
    assert configManager.get(config, section, option) == expected

@flaky(3,1)
@pytest.mark.parametrize('value, expected', data_getBoolean())
def test_getBoolean(value, expected):
    config = configManager.getConfig()
    configManager.set(config, "TEST-SEC", "TEST-OP", value)
    assert configManager.getboolean(config, "TEST-SEC", "TEST-OP") == expected
    assert configManager.getboolean(config, "TEST", "TEST-OP") is None

@flaky(3,1)
@pytest.mark.parametrize('section, option, value', data_set())
def test_set(section, option, value):
    config = configManager.getConfig()
    configManager.set(config, section, option, value)
    assert configManager.get(config, section, option) == value

@flaky(3,1)
@pytest.mark.parametrize('section', data_setSection())
def test_setSection(section):
    config = configManager.getConfig()
    configManager.setSection(config, section)
