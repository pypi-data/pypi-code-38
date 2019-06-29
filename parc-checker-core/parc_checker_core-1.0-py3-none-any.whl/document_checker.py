from parc_checker_core.action import Action

class DocumentChecker:

    def __init__(self, doc_type):
        self._check_tasks = []
        self._doc_type = doc_type

    def __call__(self, request, response, action):
        return self.run(request, response, action)

    def add_task(self, task):
        self._check_tasks.append(task)

    def get_doc_type():
        return self._doc_type

    def reset(self):
        self._check_tasks = []

    def run(self, request, response, action):
        switcher = {
            Action.GET: self.on_get,
            Action.CREATE: self.on_create,
            Action.UPDATE: self.on_update,
            Action.DELETE: self.on_delete,
            Action.CHANGE_MAIN_CP: self.on_change_cp
            }

        action_function = switcher.get(action, lambda: "The requestion action is not implemented")
        action_function(request, response)
        return self._check_tasks
