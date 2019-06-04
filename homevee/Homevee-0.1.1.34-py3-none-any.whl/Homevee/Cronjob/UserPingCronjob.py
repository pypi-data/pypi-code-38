from platform import system as system_name  # Returns the system/OS name
from subprocess import call   as system_call  # Execute a shell command

from Homevee.Cronjob import IntervalCronjob
from Homevee.Helper import Logger
from Homevee.Utils.Database import Database


class UserPingCronjob(IntervalCronjob):
    def __init__(self):
        super(UserPingCronjob, self).__init__(task_name="UserPingCronjob", interval_seconds=15)

    def task_to_do(self, *args):
        #self.ping_users()
        pass

    def ping_users(self):
        db = Database()

        items = db.select_all("SELECT * FROM USERDATA", {})

        for item in items:
            ip = item['IP']

            Logger.log("Pinging user: "+item['USERNAME'])

            last_val = item['AT_HOME']

            at_home = self.ping(ip)

            #if last_val != at_home:
            #   trigger automation

            if at_home:
                Logger.log(item['USERNAME']+ ": at home")
            else:
                Logger.log(item['USERNAME']+ ": not at home")

            db.update("UPDATE USERDATA SET AT_HOME = :at_home WHERE USERNAME = :user",
                        {'at_home': at_home, 'user': item['USERNAME']})

    def ping(self, host):
        """
        Returns True if host (str) responds to a ping request.
        Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
        """

        # Ping command count option as function of OS
        param = '-n' if system_name().lower()=='windows' else '-c'

        # Building the command. Ex: "ping -c 1 google.com"
        command = ['ping', param, '1', host]

        # Pinging
        return system_call(command) == 0