import os
import pytest
import logging
import Utils.logManager as logManager
import RaveEngine.configManager as configManager
import RaveEngine.projectManager as projectManager
import Utils.commandManager as commandManager
import Utils.sad as sad
from flaky import flaky

logger = logging.getLogger(__name__)

@pytest.fixture(autouse=True)
def setup():
    projectManager.createInitProject()
    yield
    commandManager.runRmDirCommand(sad._CONFIG_DIR_NAME_)
    commandManager.runRmDirCommand(sad._LOG_DIR_NAME_)
    commandManager.runRmDirCommand(sad._MODULES_DIR_)

@flaky(3,1)
def test_verbose():
    assert logManager._verbose()
    config = configManager.getConfig()
    configManager.set(config, sad._CONFIG_RAVEGEN_SECTION_, sad._CONFIG_VERBOSE_OPTION_, "no")
    assert not logManager._verbose()
    commandManager.runRmDirCommand(sad._CONFIG_DIR_NAME_)
    assert logManager._verbose()
    commandManager.runMkdirCommand(sad._CONFIG_DIR_NAME_)
    assert logManager._verbose()
    commandManager.runTouchCommand(sad._CONFIG_FILE_PATH)
    assert logManager._verbose()
    configFile = open(sad._CONFIG_FILE_PATH, 'w')
    configFile.write("[RaveGen]\n")
    configFile.close()
    assert logManager._verbose()

@flaky(3,1)
def test_log():
    assert logManager._log()
    config = configManager.getConfig()
    configManager.set(config, sad._CONFIG_RAVEGEN_SECTION_, sad._CONFIG_LOG_OPTION_, "no")
    assert not logManager._log()
    commandManager.runRmDirCommand(sad._CONFIG_DIR_NAME_)
    assert not logManager._log()
    commandManager.runMkdirCommand(sad._CONFIG_DIR_NAME_)
    assert not logManager._log()
    commandManager.runTouchCommand(sad._CONFIG_FILE_PATH)
    assert logManager._log()
    configFile = open(sad._CONFIG_FILE_PATH, 'w')
    configFile.write("[RaveGen]\n")
    configFile.close()
    assert logManager._log()

@flaky(3,1)
def test_printVerbose(capsys):
    logManager.printVerbose("TEST")
    captured = capsys.readouterr()
    assert captured.out == "TEST\n"
    config = configManager.getConfig()
    configManager.set(config, sad._CONFIG_RAVEGEN_SECTION_, sad._CONFIG_VERBOSE_OPTION_, "no")
    logManager.printVerbose("TEST")
    captured = capsys.readouterr()
    assert captured.out == ""

@flaky(3,1)
def test_printLog():
    config = configManager.getConfig()
    configManager.set(config, sad._CONFIG_RAVEGEN_SECTION_, sad._CONFIG_LOG_OPTION_, "no")
    logManager.printLog("TEST")
    assert os.path.exists(sad._LOG_FILE_PATH_)
    logFile = open(sad._LOG_FILE_PATH_, 'r')
    line = logFile.readline()
    logFile.close()
    assert not line
    configManager.set(config, sad._CONFIG_RAVEGEN_SECTION_, sad._CONFIG_LOG_OPTION_, "yes")
    logManager.printLog("TEST")
    logFile = open(sad._LOG_FILE_PATH_, 'r')
    line = logFile.readline()
    logFile.close()
    line = line.split(":")
    assert line[3] == " TEST\n"

@flaky(3,1)
def test_printConsole(capsys):
    logManager.printConsole("TEST")
    captured = capsys.readouterr()
    assert captured.out == "TEST\n"
