from functools import wraps
from copy import deepcopy
from eeve.variable import VariableGroup
from eeve.taskinfo import TaskInfo
from typing import List

import travel_backpack
import sys
global_variables = VariableGroup()
global_variables['stdout'] = sys.stdout


def action_wrapper(actions: 'List[Action]', debug=False, verbose=1):
    task_variables = VariableGroup()

    def start_task(**kwargs):
        if verbose > 0:
            print('task start')
        local_variables = VariableGroup()

        task_info = TaskInfo(actions=actions, global_variables=global_variables, task_variables=task_variables, local_variables=local_variables)

        local_variables.update(kwargs)

        #from pprint import pprint
        #pprint(task_info.__dict__)

        while task_info.current_action_index < len(task_info.actions):
            task_info.increment_action_index = True
            action = task_info.actions[task_info.current_action_index]
            if verbose > 0:
                print(f'executing action {task_info.current_action_index}: {action.name}')
            _run_args = list(deepcopy(action.run_args))
            _run_kwargs = deepcopy(action.run_kwargs)
            if debug: print('------------------------------------------------------------processing act', action)

            for i, arg in enumerate(_run_args):
                if type(arg) is str:
                    if debug: print('------------------------------------------------------------processing arg', arg)
                    if arg.startswith('var$') or arg.startswith('$'):
                        _run_args[i] = task_info.get_var(arg)

            for k, v in _run_kwargs.items():
                if type(v) is str:
                    if debug: print('------------------------------------------------------------processing kwarg', v)
                    if v.startswith('var$') or v.startswith('$'):
                        _run_kwargs[k] = task_info.get_var(v)

            #print('updating task info')
            action.update_task_info(task_info)
            if debug:
                print('call:', action.name, _run_args, _run_kwargs)
            run_result = action.run(*_run_args, **_run_kwargs)

            if type(run_result) is dict:
                local_variables.update(run_result)

            if task_info.increment_action_index:
                task_info.current_action_index += 1

        if verbose > 0:
            print('task end with index', task_info.current_action_index)
            print()

    return travel_backpack.except_and_print(travel_backpack.thread_encapsulation(start_task))
