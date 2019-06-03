class Task:
    def __init__(self, section_name, task_name, default, commands):
        self.section_name = section_name
        self.task_name = task_name
        self.default = default
        self.script_commands = commands

    def __repr__(self):
        return "Section: %s\nTask: %s\nDefault: %s\n - %s" % (self.section_name,
                                                              self.task_name,
                                                              self.default,
                                                              "\n - ".join(self.script_commands)
                                                              )
