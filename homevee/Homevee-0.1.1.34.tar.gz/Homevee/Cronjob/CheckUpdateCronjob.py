from Homevee.Cronjob import IntervalCronjob
from Homevee.Updater import Updater


class CheckUpdateCronjob(IntervalCronjob):
    def __init__(self):
        super(CheckUpdateCronjob, self).__init__(task_name="CheckUpdateCronjob", interval_seconds=60*60)

    def task_to_do(self, *args):
        self.check_for_updates()

    def check_for_updates(self):
        new_version = Updater().get_homevee_update_version()

        #notify user

        #check if auto update is enabled and update accordingly