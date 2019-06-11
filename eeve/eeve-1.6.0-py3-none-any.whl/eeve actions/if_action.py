from eeve.taskinfo import TaskInfo


class IfAction:
    def run(self, *args, logic='AND', inverse=False, **kwargs):
        #print('if statement')
        self.logic = logic.lower()
        if hasattr(self, 'info'):
            name = self.info.actions[self.info.current_action_index].name
        else:
            name = 'end if'

        if (name == 'if' or name == 'else') and name != 'end if':
            result = self.check_args(args, kwargs)
            if name == 'else':
                result = False
            if inverse:
                result = not result
            if not result:  # if condition resolves to false
                if_count = 1
                for i, action in self.info.get_next_actions():
                    if action.name == 'else':
                        if_count -= 1

                    elif action.name == 'end if':
                        if_count -= 1
                    elif action.name == 'if':
                        if_count += 1
                    print('\t', i, action.name, '- lv', if_count)

                    if if_count == 0:
                        self.info.current_action_index = i
                        print(f' ==> jump to {i}:', action.name)
                        if action.name == 'else':
                            self.info.current_action_index = i + 1
                        break

                else:  # if didn't hit break statement
                    self.info.current_action_index = len(self.info.actions)

                self.info.increment_action_index = False

    def set_task_info(self, info: TaskInfo):
        #print('info set')
        self.info = info

    def check_args(self, args, kwargs):
        resolves = []
        for arg in args:
            resolves.append(bool(arg))

        for k, v in kwargs.items():
            resolves.append(self.info.get_var(k) == self.info.get_var(v))

        mapping = {'and': (True, lambda x, y: x and y), 'or': (False, lambda x, y: x or y), 'xor': (False, lambda x, y: x ^ y)}
        result = mapping.get(self.logic, [True])[0]
        for i in resolves:
            result = mapping[self.logic][1](result, i)
        return result


actions = {
    'if': {
        'class': IfAction,
        'task_info': IfAction.set_task_info
    },
    'else': {
        'class': IfAction,
        'task_info': IfAction.set_task_info
    },
    'end if': IfAction
}
