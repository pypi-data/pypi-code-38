import datetime
import json
import time
import logging
import boto3
import os
import sys
from prettytable import PrettyTable
from pytz import timezone
from pprint import pprint
from os import system
from ..display import DisplayData
from .CloudWatchlogsAnsible import Ansiblelogs
# to run test uncomment this  and comment 2 line above this
# sys.path.insert(0,'../Services')
# from cloudwatch.CloudWatchlogsAnsible import Ansiblelogs
# from display import DisplayData


PATH = os.environ['HOME']
PATH += "/ReferReferencofLogGrop"
FILEPATH = PATH + '/ReferencofLogGrop.json'

if not os.path.isdir(PATH):
    os.mkdir(PATH)


def prGreen(skk):
    return("\033[92m {}\033[00m" .format(skk))


def prCyan(skk):
    return("\033[96m {}\033[00m" .format(skk))


def prRed(skk):
    return("\033[91m {}\033[00m" .format(skk))


def prYellow(skk):
    return("\033[93m {}\033[00m" .format(skk))


def help():
    """
        Display help
    """
    t = PrettyTable(['Command No', 'Description'])
    t.add_row(["logs", prCyan("To Configure")])
    t.add_row(["logs -help", prCyan("To View help")])
    t.add_row(["logs -t [shorthand] -starttime [2019-05-25_15:30:5]",
               prCyan("To view logs realtime ")])
    t.add_row(["logs -t [shorthand] -time ",
               prCyan("To view time of which the logs are fetching")])
    print(t)


def Configure():
    """
        Calles when we need to configure  the logs service fucntion perform follwing task
        1.shows logs
        2.shows reference logs
        3.add reference logs
        4.show help 
        parameter :
                None
        return :
                None
    """
    object = GetCloudWatchLogs()
    while True:
        print("Press Enter to Continoue")
        s = sys.stdin.read(1)
        system('clear')
        print(s)
        t = PrettyTable(['Command No', 'Description'])
        t.add_row(["1", prCyan("For Display ReferencofLogGrop")])
        t.add_row(["2", prCyan("Display all logGroup")])
        t.add_row(["3", prCyan("Add ReferencofLogGrop")])
        t.add_row(["4", prCyan("To View help")])
        print(t)
        print(
            prCyan("To View Logs \nRun Follwing Command Directly") +
            "\n[shorthand] prod")
        print(prRed("Type 99 To Exit \n"))
        userInput = input("Enter The following Option:- ")
        print(":-", userInput)
        if(isinstance(userInput, str)):
            # print(userInput in object.ReferencOfLogGroup.keys())
            if (userInput in object.ReferencOfLogGroup.keys()):
                object.TailLogGroup(userInput, displaytime=True)
            else:
                try:
                    userInput = int(userInput)
                except Exception as _:
                    print(
                        prRed('Enter proper Short hand, \
                            Press 1  to see all shorthands'))
                    pass

        if userInput == 1:
            object.DisplayReferencOfLogGroup()
        elif userInput == 2:
            userInput = input("Enter Region Name default:-us-west-2 :- ")
            if userInput == '':
                userInput = 'us-west-2'
            object.ListLogs(region_name=userInput)
            DisplayData.DisplayList(object.ledger)
            # object.DisplayLogs()
        elif userInput == 3:
            key = input("Short hand term for loggroup:- ")
            userInput = input("Enter Region Name default:-us-west-2 :- ")
            if userInput == '':
                userInput = 'us-west-2'
            object.ListLogs(region_name=userInput)

            data = object.ledger
            output = DisplayData.DisplayList(data)
            object.AddReferencOfLogGroup(key, output)
            object.TailLogGroup(key, displaytime=True)
        elif userInput == 99:
            print("Thank You for Using DevCloud © -" + prRed('axion1997'))
            exit()
        elif userInput == 4:
            help()


class GetCloudWatchLogs():
    """
        Base class for the cloudwatch logs contains function
        :LoadReferencOfLogGroup
        :DisplayReferencOfLogGroup
        :AddReferencOfLogGroup
        :ListLogs
    """
    def __init__(self):
        self.ledger = []
        self.ReferencOfLogGroup = self.LoadReferencOfLogGroup()
        self.client = 1

    def LoadReferencOfLogGroup(self):
        """
            open file and Load all the reference logs and store it in self.ReferencOfLogGroup
            parameter :None
            return : Nonw
        """
        try:
            File = open(FILEPATH, 'r')
            ReferencOfLogGroup = json.loads(File.read())
            return ReferencOfLogGroup
        except Exception as _:
            return {}

    def DisplayReferencOfLogGroup(self):
        """
            prints refernce logs present in self.ReferencOfLogGroup
            parameter :None
            return :None
        """
        try:
            File = open(FILEPATH, 'r')
            ReferencOfLogGroup = json.loads(File.read())
            print(prGreen('-') * 10)
            for k, v in ReferencOfLogGroup.items():
                print(prGreen(k), '\t', v)
            print(prGreen('-') * 10)
        except Exception as _:
            pass

    def AddReferencOfLogGroup(self, key, output):
        """
            add shorthand and log group in refernce logs and store it in file path 
            parameter:key (str) -> shorthand
                    output(dict)-> "loggroup  and region"
            return : None
        """
        try:
            File = open(FILEPATH, 'r')
            ReferencOfLogGroup = json.loads(File.read())
            File.close()
        except Exception as _:
            ReferencOfLogGroup = {}

        ReferencOfLogGroup[key] = output
        File = open(FILEPATH, 'w')
        a = json.dumps(ReferencOfLogGroup, indent=4, sort_keys=True)
        File.write(a)
        File.close()
        return True

    def ListLogs(self, region_name):
        """
            Fetch all log group from the specified region 
            parameter:region_name(str) -> region_name
            return : None
            Note : 
                Stores data in self.ledger
        """
        try:
            self.client = boto3.client('logs', region_name=region_name)
            response = self.client.describe_log_groups()
            self.ledger.clear()
            for data in response['logGroups']:
                self.ledger.append(
                    {'Name': data['logGroupName'], 'region': region_name})

            if 'nextToken' in response:
                res = response['nextToken']
                while res:
                    response = self.client.describe_log_groups(
                        nextToken=res,
                        limit=50
                    )
                    for data in response['logGroups']:
                        self.ledger.append(
                            {'Name': data['logGroupName'], 'region': region_name})
                    if 'nextToken' not in response:
                        break
                    else:
                        res = response['nextToken']
        except Exception as identifier:
            return False

    def GetshorthandValue(self, shorthand):
        """
            Fetch value of shorthand fron the File containg all shorthand and their value
            parameter:shorthand(str) -> shorthand
            return : dict ->
            {
                logGroup:(str)
                region_name:(str)
            }
            Note : 
                Chalta hai        
        """
        try:
            File = open(FILEPATH, 'r')
            ReferencOfLogGroup = json.loads(File.read())
            File.close()
            return(ReferencOfLogGroup[shorthand])
        except Exception as _:
            raise Exception("Enter Proper Shorthand")

    def Checkregion(self, region_name):
        """
            Checksregion and return time fucntion
            parameter:region_name(str) -> region_name
            return : Refernce of a function ->
            Note : 
                Chalta hai        
        """
        if region_name == 'us-west-2':
            return datetime.datetime.utcnow
        elif region_name == 'ap-south-1':
            return datetime.datetime.now
        else:
            return datetime.datetime.utcnow

    def checkepoch(self, startTime, region_name):
        """
            Checksr egion and return epoch i.e start_time fucntion
            parameter:region_name(str) -> region_name
            return : return epoch i.e start_time
            Note : 
                Chalta hai        
        """
        if region_name == 'us-west-2':
            startTime = startTime + 19800
            return startTime
        elif region_name == 'ap-south-1':
            return startTime
        else:
            startTime = startTime + 19800
            return startTime

    def TailLogGroup(self, shorthand,
                     startTime=None,
                     endTime=None,
                     displaytime=None):
        """
        Tails loggroup 
        paramerter:
            shorhand(str) -> Shorthand
            startTime(bool) -> startTime
            endTime (bool)
            displaytime(bool)
        return:
            none
        """
        try:
            data = self.GetshorthandValue(shorthand)
        except Exception as _:
            print("Enter Proper Shorthand\n")
            Configure()

        region_name = data['region']
        logGName = data['Name']
        gettime = self.Checkregion(region_name)
        if startTime is None:
            STime = gettime()
            startTime = int(STime.strftime('%s'))
            currenttime = int(gettime().strftime('%s'))
            print(logGName, " Is started to tail from ", time.ctime(startTime))
        elif startTime is not None:
            print(startTime)
            currenttime = int(gettime().strftime('%s'))
            epo = datetime.datetime.strptime(startTime, "%Y-%m-%d_%H:%M:%S")
            startTime = int(epo.strftime('%s'))
            print(startTime)

        while True:
            t1 = time.time()
            self.client = boto3.client('logs', region_name=region_name)

            response = self.client.filter_log_events(
                logGroupName=logGName,
                startTime=(startTime - 30) * 1000,
                endTime=currenttime * 1000
            )
            # pprint(response)
            if displaytime:
                var = self.checkepoch(startTime, region_name) - 10
                var2 = self.checkepoch(currenttime, region_name)
                timetoshow = time.ctime(var) + "-" + time.ctime(var2) + \
                    "-" + str(len(response['events']))
                # print(time.ctime(self.checkepoch(startTime,region_name)-10),'-',time.ctime(self.checkepoch(currenttime,region_name)),len(response['events']))
                print(prYellow(timetoshow))

            for data in response['events']:
                print(data['message'])

            # print(time.ctime(self.checkepoch(startTime,region_name)-10),'-',time.ctime(self.checkepoch(currenttime,region_name)),len(response['events']))
            # STime = gettime()
            startTime = startTime + 10  # int(STime.strftime('%s'))
            # startTime = #int(STime.strftime('%s'))
            currenttime = startTime

            deta = 10 - (time.time() - t1)
            if(deta <= 0):
                pass
            else:
                time.sleep(deta)

    def AnsibleLogs(self, argument):
        """
            used Explestly for ansible
            parameter
                argument(list[str]) : ['diviceId','data','time']
            return:
                none
            Note:
                Ansible only
        """
        obj = Ansiblelogs()
        controllerId, timestamp = obj.processArgument(argument)
        taskid = obj.getTaskId(controllerId, timestamp)
        obj.fechLogsFromStartAndTail(taskid)

    def DisplayLogs(self):
        """
            Note: - Display loggroup
            Par nahi call hota hai ye function 
        """
        t = PrettyTable(['Sr', 'LogGroupName', 'Region'])
        for i in range(len(self.ledger)):
            t.add_row([i, self.ledger[i]['Name'], self.ledger[i]['region']])
        print(t)


def ArgumentforCloudwatch(argument):
    """
    Main function of the Client Entry point of the logs service
    Determine fuctio to call 

    parametre(list):[-t,'str]
                    contain Ansible support
    return :
            None
    Note:
        doesn't return calles the respective argument 
    """
    # argument = sys.argv[1:]
    print("ArgumentforCloudwatch", argument, len(argument))
    length = len(argument)
    if length == 0:
        Configure()
    elif argument[0] == '-help':
        help()
    elif argument[0] == '-t':
        print("k")
        # print(length)
        if length == 2:
            object = GetCloudWatchLogs()
            shorthand = argument[1]
            object.TailLogGroup(shorthand)
        elif length == 3:
            if argument[2] == '-time':
                shorthand = argument[1]
                object = GetCloudWatchLogs()
                object.TailLogGroup(shorthand, displaytime=True)
        elif length == 4:
            argument[2] == '-starttime'
            short = argument[1]
            startTime = argument[3]
            object = GetCloudWatchLogs()
            object.TailLogGroup(shorthand=short, startTime=startTime)
        elif length == 5:
            object = GetCloudWatchLogs()
            object.AnsibleLogs(argument[2:])
        else:
            return('wrong')
    else:
        return('wrong')

# if __name__ == "__main__":
#     try:
#         # Configure()
#         argument = sys.argv[1:]
#         print(argument,len(argument))
#         length = len(argument)
#         if length == 0:
#             Configure()
#         elif argument[0] == '-help':
#             help()
#         elif argument[0] == '-t':
#             print("k")
#             # print(length)
#             if length == 2:
#                 shorthand = argument[1]
#                 object = GetCloudWatchLogs()
#                 object.TailLogGroup(shorthand)
#             elif length == 3 :
#                 if argument[2] == '-time':
#                     shorthand = argument[1]
#                     object = GetCloudWatchLogs()
#                     object.TailLogGroup(shorthand,displaytime=True)
#             elif length == 4 :
#                 argument[2] == '-starttime'
#                 short = argument[1]
#                 startTime = argument[3]
#                 object = GetCloudWatchLogs()
#                 object.TailLogGroup(shorthand=short ,startTime=startTime)
#             else:
#                 print('wrong')

#     except Exception as identifier:
#         logging.exception(identifier)
#         # python3 CloudWatchlogs.py -t 5 now
#         # python3 CloudWatchlogs.py -list
#         # python3 CloudWatchlogs.py -t 5 2019-05-25 15:30:5
