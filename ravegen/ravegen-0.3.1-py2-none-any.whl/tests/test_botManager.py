import pytest
import os
import RaveEngine.projectManager as projectManager
import RaveEngine.botManager as botManager
import RaveEngine.configManager as configManager
import Utils.commandManager as commandManager
from flaky import flaky
import Utils.sad as sad
import Utils.utils as utils

@pytest.fixture(autouse=True)
def setup():
    projectManager.createInitProject(createBasicModules=True)
    yield
    commandManager.runRmDirCommand(sad._CONFIG_DIR_NAME_)
    commandManager.runRmDirCommand(sad._LOG_DIR_NAME_)
    commandManager.runRmDirCommand(sad._MODULES_DIR_)
    commandManager.runRmDirCommand(sad._OUTPUT_BOT_DIR_)

def data_generateHeaders():
    return [sad._HEADER_TOKEN_FLAG]

def data_generateBot():
    data = [(False, sad._HOSTING_HEROKU_OPTION_), (True, sad._HOSTING_HEROKU_OPTION_)]
    data += [(False, sad._HOSTING_GAE_OPTION_), (True, sad._HOSTING_GAE_OPTION_)]
    return data

@flaky(3,1)
@pytest.mark.parametrize('testFlag, hosting', data_generateBot())
def test_generateBot(testFlag, hosting):
    projectManager.createInitProject(createBasicModules=True, hostingOption=hosting)
    if not testFlag:
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            botManager.generateBot(testFlag=testFlag)
        assert pytest_wrapped_e.type == SystemExit
        config = configManager.getConfig()
        configManager.set(config, sad._CONFIG_RAVEGEN_SECTION_, sad._CONFIG_DEPLOY_URL_OPTION, "www.test.com")
    botManager.generateBot(testFlag=testFlag)
    assert os.path.exists(sad._OUTPUT_BOT_DIR_)
    assert os.path.exists(sad.OUTPUT_BOT_PATH)
    headers = utils._getHeaders()
    if testFlag:
        assert headers[sad._HEADER_TOKEN_FLAG] == sad._STR_TRUE_
    else:
        assert headers[sad._HEADER_TOKEN_FLAG] == sad._STR_FALSE_

@flaky(3,1)
@pytest.mark.parametrize('header', data_generateHeaders())
def test_generateHeaders(header):
    botManager.generateBot()
    headers = utils._getHeaders()
    assert header in headers
