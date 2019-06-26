import os
from datetime import datetime

from pytz import timezone


class Tool:
    def __init__(self, base=os.path.join("..", "storage")):
        self.base = base

    @staticmethod
    def get_est():
        ts = datetime.now()
        est = ts.astimezone(timezone('US/Eastern'))
        f_date = est.strftime('%Y%m%d')
        return f_date

    def choose_folder(self):
        current = self.get_est()
        path = os.path.join(self.base, current)
        if not os.path.exists(path):
            os.makedirs(path)
        return path
