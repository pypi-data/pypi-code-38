from eeve.variable import Variable, get_var_name
from datetime import datetime


class SetVar:
    def __init__(self):
        self.info = None

    def run(self, var: str, value, *args):
        if value == '{now}':
            value = datetime.now()
        elif value.startswith('{expression:') and value.endswith('}'):
            value = value[12:-1]  # remove the beggining and last }
            value.format(*args)
            value = eval(value)

        self.info.get_var(get_var_name(var)).value = value

    def set_task_info(self, info: 'TaskInfo'):
        #print('info set')
        self.info = info


actions = {'set variable': {'class': SetVar, 'task_info': SetVar.set_task_info}}
