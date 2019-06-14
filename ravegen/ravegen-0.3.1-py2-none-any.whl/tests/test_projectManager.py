import os
import pytest
import RaveEngine.projectManager as projectManager
import Utils.sad as sad
import Utils.commandManager as commandManager
import RaveEngine.configManager as configManager
from flaky import flaky

TOKEN_TEST = "TOKEN_TEST"

@pytest.fixture(autouse=True)
def setup():
    yield
    commandManager.runRmDirCommand(sad._CONFIG_DIR_NAME_)
    commandManager.runRmDirCommand(sad._LOG_DIR_NAME_)
    commandManager.runRmDirCommand(sad._MODULES_DIR_)

@flaky(3,1)
@pytest.mark.parametrize('TOKEN', [(None), (TOKEN_TEST)])
def test_createInitProject(TOKEN):
    projectManager.createInitProject(TOKEN=TOKEN, TOKEN_TEST=TOKEN)
    assert os.path.exists(sad._CONFIG_DIR_NAME_)
    assert os.path.exists(sad._MODULES_DIR_)
    assert os.path.exists(sad._LOG_DIR_NAME_)
    assert os.path.exists(sad._LOG_FILE_PATH_)
    assert os.path.exists(sad._CONFIG_REQ_FILE_PAHT_)
    assert os.path.exists(sad._CONFIG_RUNTIME_FILE_PATH_)
    projectManager.createInitProject(TOKEN=TOKEN, TOKEN_TEST=TOKEN, hostingOption=sad._HOSTING_GAE_OPTION_)
    if TOKEN:
        config = configManager.getConfig()
        tempToken = configManager.get(config, sad._CONFIG_RAVEGEN_SECTION_, sad._CONFIG_TOKEN_OPTION_)
        tempTokenTest = configManager.get(config, sad._CONFIG_RAVEGEN_SECTION_, sad._CONFIG_TOKEN_TEST_OPTION)
        assert tempToken == TOKEN
        assert tempTokenTest == TOKEN


@flaky(3,1)
def test_createBasicModules():
    projectManager.createInitProject(createBasicModules=True)
    assert os.path.exists(sad._MODULES_DIR_ + sad._DF_ + "start.py")
    assert os.path.exists(sad._MODULES_DIR_ + sad._DF_ + "echo.py")
    assert os.path.exists(sad._MODULES_DIR_ + sad._DF_ + "caps.py")
    assert os.path.exists(sad._MODULES_DIR_ + sad._DF_ + "error.py")
    assert os.path.exists(sad._MODULES_DIR_ + sad._DF_ + "buttons.py")
