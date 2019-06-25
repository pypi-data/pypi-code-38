import SerialUI

import readline # optional, will allow Up/Down/History in the console
import code
import rlcompleter
readline.parse_and_bind("tab: complete")


def runInterpreter(extraVars=None):
    variables = globals()
    variables.update(locals())
    if extraVars is not None:
        variables.update(extraVars)
    shell = code.InteractiveConsole(variables)
    shell.interact()


