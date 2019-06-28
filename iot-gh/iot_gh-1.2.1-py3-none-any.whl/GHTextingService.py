# Author: Keith E. Kelly - 1/12/2019
import threading
import requests
import time
import csv
import pigpio

class GHTextMessage(object):
    id = None
    name = None
    text = None
    commands = None

class GHTextingService(threading.Thread):
    BASE_URL = "https://api.groupme.com/v3"
    
    def __init__(self, access_token, greenhouse_service = None ,group_name = "iot_greenhouse", bot_name = "gh"):
        threading.Thread.__init__(self)
        self._access_token = access_token
        self.ghs = greenhouse_service
        self._group_name = group_name
        self._bot_name = bot_name
        if type(self.ghs._pi) is not pigpio.pi: #debug mode. Load test file
            self._load_command_file("./GHTextingServiceCommands.csv")
        else:
            conf_file = os.path.expanduser("~/.iot_gh/GHTextingServiceCommands.csv")
            self._load_command_file(conf_file)
        #self._load_command_file("GHTextingServiceCommands.csv")
        #self._load_command_file("/home/gh/.local/lib/python3.5/site-packages/iot_gh/GHTextingServiceCommands.csv")
       
        self._group_id = self._get_group_id()
        if self._group_id == None:
            self._group_id = self._make_group()
        self._bot_id = self._get_bot_id()
        if self._bot_id == None:
            self._bot_id = self._make_bot()
        self._send_intro_message()
        self._last_scanned_message_id = self._get_last_scanned_message_id()
        
        self.daemon = True
        self.start()

    def run(self):
        while True:
            next_commands = self._get_next_commands()
            if next_commands != None:
                self._execute_commands(next_commands)
            time.sleep(2)

    def _get_group_id(self):
        group_id = None
        params = {"token": self._access_token}
        headers = {"content-type": "application/json"}
        end_point = "/groups"
        url = "%s%s" % (self.BASE_URL, end_point)
        r = requests.get(url, headers=headers, params=params)
        if r.status_code != 200:
            raise Exception("Bad request. Unable to fetch group. Please verify your access token." + r.text)
        else:
            groups = r.json()["response"]
            for group in groups:
                if group["name"] == self._group_name:
                    group_id = group["id"]
                    break
        return group_id
    
    def _make_group(self):
        group_id = None
        params = {"token": self._access_token}
        payload = {"name": self._group_name} 
        headers = {"content-type": "application/json"}
        end_point = "/groups"
        url = "%s%s" % (self.BASE_URL, end_point)
        r = requests.post(url, headers=headers, params=params, json=payload)
        if r.status_code != 201:
            raise Exception("Bad request. Unable to create group. " + r.text)
        else:
            group = r.json()["response"]
            group_id = group["id"]
        return group_id

    def _get_bot_id(self):
        bot_id = None
        #payload = {"group_id": self._group_id}
        headers = {"content-type": "application/json"}
        end_point = "bots"
        url = "%s/%s?token=%s" % (self.BASE_URL, end_point, self._access_token)
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            raise Exception("Bad request. Unable to fetch bot id. " + r.text)
        else:
            bots = r.json()["response"]
            for bot in bots:
                if bot["name"] == "gh" and bot["group_id"] == self._group_id:
                    bot_id = bot["bot_id"]
                    break
        return bot_id

    def _make_bot(self):
        bot_id = None
        payload = {"bot": {"name": "gh", "group_id": self._group_id}} 
        headers = {"content-type": "application/json"}
        #url = self.BASE_URL + "/bots?token=" + self._access_token
        end_point = "bots"
        url = "%s/%s?token=%s" % (self.BASE_URL, end_point, self._access_token)
        r = requests.post(url, json=payload, headers=headers)
        if r.status_code != 201:
            raise Exception("Bad request. Unable to create bot. " + r.text)
        else:
            bot = r.json()["response"]["bot"]
            bot_id = bot["bot_id"]
        return bot_id

    def _send_message(self, message):
        payload = {"bot_id": self._bot_id, "text": message}
        headers = {"content-type": "application/json"}
        end_point = "bots/post"
        url = "%s/%s?token=%s" % (self.BASE_URL, end_point, self._access_token)
        r = requests.post(url, json=payload, headers=headers)
        if r.status_code != 202:
            raise Exception("Unable to post message. " + r.text)
        else:
            self.last_message = GHTextMessage()
            self.last_message.id = str(time.time())
            self.last_message.name = "gh"
            self.last_message.text = message
        
    def _send_intro_message(self):
        m = "Hello. Send me a direct message (@gh) with the text '#help' for a list of IoT Greenhouse text commands. Use '#help-verbose' for detailed help text."
        self._send_message(m)

    
    def _get_last_scanned_message_id(self):
        last_message_id = None
        params = {"token": self._access_token}
        params["limit"] = 1  
        headers = {"content-type": "application/json"}
        end_point = "/groups/%s/messages" % self._group_id
        url = "%s%s" % (self.BASE_URL, end_point)
        r = requests.get(url, headers=headers, params=params)
        if r.status_code != 200:
            raise Exception("Unable to fetch messages. " + r.text)
        else:
            messages= r.json()["response"]["messages"]
            if len(messages) > 0:
                last_message_id = messages[0]["id"]
            else:
                raise Exception("No last message fount. " + r.text)

        return last_message_id
    
    def _get_next_commands(self):
        commands = None
        params = {"token": self._access_token}
        params["after_id"] = self._last_scanned_message_id  
        headers = {"content-type": "application/json"}
        end_point = "/groups/%s/messages" % self._group_id
        url = "%s%s" % (self.BASE_URL, end_point)
        r = requests.get(url, headers=headers, params=params)
        if r.status_code != 200:
            raise Exception("Unable to fetch messages. " + r.text)
        else:
            messages= r.json()["response"]["messages"]
            count = len(messages)
            if count > 0:
                self._last_scanned_message_id = messages[count-1]["id"]
                for message in messages:
                    if message["text"][:3] == "@gh":
                        self._last_scanned_message_id = message["id"]
                        self.last_message = GHTextMessage()
                        self.last_message.id = message["id"]
                        self.last_message.name = message["name"]
                        self.last_message.text = message["text"]
                        s = message["text"].split()
                        if len(s) > 1:
                            s.pop(0)
                            commands = s
                            break
                        else:
                            time.sleep(1)
                            self._send_message("Sorry. I'd like to chat, but I'm only configured to response to valid IoT Greenhouse commands. Use '#help' or '#help_verbose' to see a list of valid commands.")
                
        return commands

    def _execute_commands(self, commands):
        cmds = [command.lower() for command in commands]
        cmds = [command.strip() for command in commands]
        if self._valid_commands(cmds):
            for cmd in cmds:
                m = self.command_list[cmd][2]
                if  m != "None":
                    self._send_message(m)
                c = self.command_list[cmd][0]
                if  c != "None":
                    try:
                        exec("self.%s" % c)
                    except:
                        self._send_message("Error: Invalid IoT Greenhouse command defined in command configuration file. %s" % c)
 
    def _valid_commands(self, commands):
        valid = True
        valid_commands = [self.command_list]
        for command in commands:
            if command not in self.command_list:
                self._send_message("Sorry. I'd like to chat, but I'm only configured to response to valid IoT Greenhouse commands. Use '#help' or '#help_verbose' to see a list of valid commands.")
                valid = False                
                break
        return valid

    def _load_command_file(self, filename):
        """Reads commands from CSV file
        """
        try:
            with open(filename) as csvfile:
                cmd_reader = csv.reader(csvfile, delimiter=',')
                self.command_list = {}
                for cmd in cmd_reader:
                    self.command_list[cmd[0]] = [cmd[1], cmd[2], cmd[3]] 

        except Exception as e:
            raise Exception("Unable to load commands. %s" % str(e))

    def send_command_list(self):
         m = "Valid IoT Greenhouse commands are: %s" % " ".join(self.command_list.keys() )
         self._send_message(m)

    def send_command_details(self):
        str_list = []
        str_list.append("Valid IoT Greenhouse commands are:\n\n")
        for cmd in self.command_list:
            s = "%s  %s\n" % (cmd, self.command_list[cmd][1])
            str_list.append(s)
  
        m =  "".join(str_list)
        self._send_message(m)

    def send_temperature(self):   
        temp = self.ghs.temperature.get_inside_temp_F()
        m = "Current greenhouse temperature is %s." % temp
        self._send_message(m)         

                



