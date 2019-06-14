import signal
import consoleManager as consoleManager
import RaveEngine.projectManager as projectManager
import RaveEngine.botManager as botManager
import CloudEngine.cloudManager as cloudManager
import Utils.inputManager as inputManager
import Utils.utils as utils
import Utils.sad as sad
import Utils.logManager as logManager

def initProgram(argv):
    signal.signal(signal.SIGINT, utils.sigintHandler)
    consoleManager.verifyArgs(argv)
    command = argv[1]

    if command == "help":
        consoleManager.printHelp()
    elif command == "init":
        options = consoleManager.getOptions(argv)
        TOKEN = inputManager.getInput("Bot token (given by @BotFather): ")
        TOKEN_TEST = None
        tokenTestFlag = inputManager.getYesNoAnswer("Do you want to have a test Bot? (Y/n): ")
        if tokenTestFlag:
            TOKEN_TEST = inputManager.getInput("Test Bot token (given by @BotFather): ")
            if TOKEN_TEST == "":
                TOKEN_TEST = None
        if TOKEN == "":
            TOKEN = None
        logManager.printConsole("==================================")
        logManager.printConsole("Hosting List:")
        logManager.printConsole("[1] Heroku")
        logManager.printConsole("[2] Google App Engine")
        hostingOption = int(inputManager.getInput("Please enter your numeric choice: "))
        if not options:
            projectManager.createInitProject(TOKEN=TOKEN, TOKEN_TEST=TOKEN_TEST, hostingOption=hostingOption)
        else:
            createBasicModules = False
            for option in options:
                if option == 'm':
                    createBasicModules = True
            projectManager.createInitProject(createBasicModules=createBasicModules, TOKEN=TOKEN, TOKEN_TEST=TOKEN_TEST, hostingOption=hostingOption)
    elif command == "create":
        options = consoleManager.getOptions(argv)
        testFlag = True
        for option in options:
            if option == 't':
                testFlag = True
            if option == 'd':
                testFlag = False
        botManager.generateBot(testFlag)
    elif command == "deploy":
        options = consoleManager.getOptions(argv)
        if not options:
            botManager.deployBot()
        else:
            testFlag = True
            for option in options:
                if option == 't':
                    testFlag = True
                if option == 'd':
                    testFlag = False
            botManager.deployBot(withOptions=True, testFlag=testFlag)
    elif command == "change":
        logManager.printConsole("We recommend you use a test bot instead of change command")
        options = consoleManager.getOptions(argv)
        testFlag = True
        for option in options:
            if option == 't':
                testFlag = True
            if option == 'd':
                testFlag = False
        botManager.changeState(testFlag)
    elif command == "deleteCloudBot":
        cloudManager.destroy()
    elif command == "version":
        versionFile = open(utils.getInstalationPath() + sad._DF_ + sad._RAVEGEN_SRC_PATH_ + sad._DF_ + sad._VERSION_FILE_NAME, 'r')
        line = versionFile.readline()
        version = line.split("=")[-1]
        logManager.printConsole(version)
        