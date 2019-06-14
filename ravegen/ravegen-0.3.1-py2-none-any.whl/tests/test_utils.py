import Utils.utils as utils
import Utils.commandManager as commandManager
from flaky import flaky

@flaky(3,1)
def test_file_Or_Directory_Exists():
    test_File_Name = ".testFile"
    testFile = open(test_File_Name, 'w')
    testFile.write("Test")
    testFile.close()
    assert utils.file_Or_Directory_Exists('./', test_File_Name)
    commandManager.runRmCommand(".testFile")
    assert not utils.file_Or_Directory_Exists('./', test_File_Name)

