import inspect
from agw import Automater, FailSafeException
from .util import fetch_file_argument

import cutie


class AutomatorApp(object):

    name = "Base Macro Application"

    def __init__(self, *args, ai_class=Automater):
        self.macros = list(args)
        self.ai_class = ai_class

    def add_macro(self, macro):
        self.macros.append(macro)

    def __iadd__(self, macro):
        self.macros.append(macro)
        return self

    def display_available_macros(self):
        print("Available Macros:")
        for macro in self.macros:
            #  print(f"  > {macro.name}")
            print(f"  > {macro.__doc__}")
        print("")

    def select_macro(self):
        if len(self.macros) == 1:
            return self.macros[0]
        print("")
        index = cutie.select([n.__doc__ for n in self.macros])
        print("")
        return self.macros[index]

    def run(self):
        try:
            macro = self.select_macro()

            print(f"Running {macro.__doc__} macro...")

            macro_args = inspect.getfullargspec(macro)

            if len(macro_args.args) not in (1, 2):
                raise Exception(f"Macro {macro.__name__} has an invalid signature.")

            ai = self.ai_class()
            ai.request_throttle()

            iterfile_decoration = hasattr(macro, "file_arg")

            if len(macro_args.args) == 2 and iterfile_decoration:
                filepath = fetch_file_argument(macro.file_arg)
                macro(ai, filepath)
            elif len(macro_args) == 2:
                macro(ai, filepath)
            else:
                macro(ai)

        except KeyboardInterrupt:
            print("Operation cancelled.")

        except FailSafeException:
            print("Fail Safe triggered! Operation cancelled.")

        except Exception as ex:
            print(f"Error: {ex}")
