from cleo import Command

class PatchedCommand(Command):
    def __init__(self):
        super(PatchedCommand, self).__init__()

    def ask(self, question, default):
        # since cleo has a bug that causes it not to return default values we need a wrapper that does exactly that
        output = super(PatchedCommand, self).ask(question)
        if output is None:
            output = default
        return output

    def choice(self, question, options, defaultIndex):
        # for some reason cleo can not handle arrays with 1 el so we need a workaround
        if len(options) > 1:
            output = super(PatchedCommand, self).choice(question, options, defaultIndex)
        else:
            output = options[0]

        return output

    def _castToBool(self, val):
        if isinstance(val, bool):
            return val
        return val.lower() in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh', 'yarr']
