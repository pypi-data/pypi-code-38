import sys

from quarchpy.utilities import TestCenter

# This is a singleton class, it will only ever refer to the same object
class user_interface:

    instance = None

    class __user_interface:
        def __init__(self,ui):
            if ui in ["console","testcenter"]:
                self.selectedInterface = ui
            else:
                raise ValueError("requested ui type not valid")

    def __init__(self,ui):
        # if we haven't create a user_interface object before
        if not user_interface.instance:
            # create a user interface object with our selected interface type
            user_interface.instance = user_interface.__user_interface(ui)
        # otherwise change the existing user interface object to the new type
        else:
            user_interface.instance.selectedInterface = ui

'''
def listSelection(title,message,selectionList)

    prompts the user to return a selection from the list
    list format is a comma delimited string (key1=value1,key2=value2...)
    the function will return the selected key

'''
def listSelection(title="",message="",selectionList=""):
    if user_interface.instance != None and user_interface.instance.selectedInterface == "testcenter":

        return TestCenter.testPoint("Quarch_Host.ShowGenericDialog", "Title=" + __formatForTestcenter(title),
                                "Message=" + __formatForTestcenter(message),
                                "ItemListString=" + __formatForTestcenter(selectionList));

    else: #default mode console output

        #print message
        print(message)
        print("")

        #split selection list into key=value pairs and print each value
        # first split on ','s into list of key=value pairs
        selectionList = selectionList.split(',')
        # then split each list item on '=' into a [key,value] list
        selectionList = [str(x).split("=") for x in selectionList]
        count=1
        for item in selectionList:
            # print index and value
            print(str(count) + " - " + item[1])
            count += 1

        print("")
        # Request user selection
        while (True):
            if sys.version_info.major >= 3:
                userStr = input("please select an option: ")
            else:
                userStr = raw_input("please select an option: ")

            # Validate the response
            try:
                userNumber = int(userStr)
                if (userNumber <= len(selectionList) and userNumber >= 1):
                    break
            except:
                print ("INVALID SELECTION!")

        # return the key associated with this entry
        return selectionList[userNumber-1][0]

'''
printText(text)

    prints out the specified text via the currently selected user interface

    arguments:
        text - a string of text, or a list of strings

'''
def printText(text,**kwargs):

        if user_interface.instance != None and user_interface.instance.selectedInterface == "testcenter":
            # if line is not empty
            if text.strip()!="":
                TestCenter.testPoint ("Quarch_Host.LogComment","Message=" + __formatForTestcenter(text))

        else:
            if kwargs!= {}:
                print(text,kwargs)
            else:
                print(text)
        return

'''
showDialog(title,message)

    prints a message to the user and waits for acknowledgement

'''
def showDialog(title,message):


        if user_interface.instance != None and user_interface.instance.selectedInterface == "testcenter":
            TestCenter.testPoint ("Quarch_Host.ShowDialog","Title=" + __formatForTestcenter(title),"Message=" + __formatForTestcenter(message))

        else:
            print(message)
            if sys.version_info.major >= 3:
                userStr = input("press enter to continue\n")
            else:
                userStr = raw_input("press enter to continue\n")


'''
progressBar(iteration,total)

    generate a progress bar based on the proportion of iteration to total
'''
def progressBar():
    '''
printProgressBar (iteration,total,prefix='',suffix='',decimals=1,length=100,fill='█')

    prints a text based progress bar

        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)

'''
def progressBar (iteration, total):

        if user_interface.instance != None and user_interface.instance.selectedInterface == "testcenter":
            TestCenter.testPoint ("Quarch_Host.ShowTaskProgress","Title=Task Progress", "Iteration="+str(iteration), "Total="+str(total));

        else:

            prefix = ''
            suffix = ''
            decimals = 1
            length = 100
            fill = '█'

            percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
            filledLength = int(length * iteration // total)
            bar = fill * filledLength + '-' * (length - filledLength)
            print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
            # Print New Line on Complete
            if iteration == total: 
                print()


'''
startTestBlock(text)

    prints out the specified text via the currently selected user interface

    arguments:
        text - a string of text, or a list of strings

'''
def startTestBlock(text):

        if user_interface.instance != None and user_interface.instance.selectedInterface == "testcenter":
            TestCenter.beginTestBlock(__formatForTestcenter(text))

        else:
            print("")
            print(text)
            print("")


        return

'''
endTestBlock()

    finishes the current test block in testcenter, no action in console

'''
def endTestBlock():

        if user_interface.instance != None and user_interface.instance.selectedInterface == "testcenter":
            TestCenter.endTestBlock()
        else:
            pass

        return

'''
logCalibrationResult(title,result)
'''
def logCalibrationResult(title,report):

    if user_interface.instance != None and user_interface.instance.selectedInterface == "testcenter":
        if report["result"]:
            TestCenter.testPoint("Quarch_Host.LogTestPoint", "Test=" + __formatForTestcenter(title), "Result=True",
                                 "Message=" + __formatForTestcenter(
                                     title) + " Passed, worst case: " + __formatForTestcenter(report["worst case"]))
            # add the report as comments
            for line in report["report"].splitlines():
                TestCenter.testPoint("Quarch_Host.LogComment", "Message=" + __formatForTestcenter(line))
            TestCenter.endTestBlock()
        else:

            TestCenter.testPoint("Quarch_Host.LogTestPoint", "Test=" + __formatForTestcenter(title), "Result=False",
                                 "Message=" + __formatForTestcenter(
                                     title) + " Failed, worst case: " + __formatForTestcenter(report["worst case"]))
            # add the report as comments
            for line in report["report"].splitlines():
                TestCenter.testPoint("Quarch_Host.LogComment", "Message=" + __formatForTestcenter(line))
            TestCenter.endTestBlock()
            TestCenter.testPoint("Quarch_Internal.storeFailure", "Message=" + __formatForTestcenter(title) + " Failed")

    else:
        if report["result"]:
            print("\n\t" + title + " Passed")
            print("")
            print("\tworst case: " + report["worst case"])
        else:
            print("\n\t" + title + " Failed")
            print("")
            print(report["report"])

'''
logResults(test,notes)
'''
def logResults(test,notes):

        if user_interface.instance != None and user_interface.instance.selectedInterface == "testcenter":
            TestCenter.testPoint ("Quarch_Host.ResultDialog","Test="+ __formatForTestcenter(test),"Notes=" + __formatForTestcenter(notes))

        else:
            print(notes)

        return

'''
storeDeviceInfo()
'''
def storeDeviceInfo(**kwargs):

        if user_interface.instance != None and user_interface.instance.selectedInterface == "testcenter":
            # Store the serial number from the DUT scan for logging and verification
            if 'serial' in kwargs:
                TestCenter.testPoint ("Quarch_Internal.StoreSerial","Serial="+"QTL"+kwargs['serial']);
            if 'idn' in kwargs:
                # replace line endings
                IDNString = '|'.join(kwargs['idn'].splitlines())
                TestCenter.testPoint ("Quarch_Internal.StoreDutActualIdn","Idn="+IDNString)

        # We need to provide testcenter with the information to populate the database
        else:
            pass


'''
'''
def __formatForTestcenter(text):
    # escape special characters
    # turn \' to \\'s
    text = text.replace('\\','\\\\')
    # replace line endings
    text = '|'.join(text.splitlines())
    return text
    
