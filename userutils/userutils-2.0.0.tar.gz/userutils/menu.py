"""
menu.py
File containing menu class.
This file is part of the userutils package https://github.com/Scoder12/userutils

Copyright 2019 Scoder12

Licensed under the MIT License.

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in the
Software without restriction, including without limitation the rights to use, copy,
modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the
following conditions: 

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.  

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE
OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""


class EmptyDataException(Exception): pass


class MenuItem:
    """
    Represents an item in a menu. 
    Attributes:
        desc (str): Description of the item. 
        value (any): Value to be returned. 
        choice (str): what must be typed to select it. If None, it will be chosen automatically by the Menu. Default None. 
    """
    def __init__(self, desc, value, choice=None):
        self.desc = desc
        self.value = value
        self.choice = choice


class CallbackMenuItem(MenuItem):
    """Represents an item in a menu with a callback. 

    Choice is what will need to be typed to select it in the menu. 
    desc is a short description and callback is run with args and kwargs when selected. 

    Attributes:
        desc (str): The description to be shown in the menu. 
        callback (func): The callback to be run when option is selected. 
        args (tuple): Optional arguments to be passed to the callback function. 
        kwargs (dict): Optional keyword arguments to be passed to the callback function. 
        choice (str): The string to be typed at the prompt for the option to be selected. If None, it will be chosen automatically by the Menu. Default None. 

    """
    def __init__(self, desc, callback, args=(), kwargs={},choice=None):
        """Inits MenuItem with given attributes. 

        Args:
            desc (str): The description to be shown in the menu. 
            callback (func): The callback to be run when option is selected. 
            args (tuple): Optional arguments to be passed to the callback function. 
            kwargs (dict): Optional keyword arguments to be passed to the callback function. 
            choice (str): The string to be typed at the prompt for the option to be selected. If None, a number is shown. Default None. 

        Raises:
            TypeError: when args is not a tuple. Commonly caused by forgetting a comma with only one argument
        """
        self.desc = desc
        self.callback = callback
        if type(args) != tuple:
            raise TypeError('args should be a tuple, not ' + str(type(args)) + ' like this: (something,)')
        self.args = args
        self.kwargs = kwargs
        self.choice = choice

    def run(self):
        """Runs the item's callback with its args and kwargs. """
        self.callback(*self.args, **self.kwargs)


class Menu:
    """A menu to let users choose what they want to do.  

    Every aspect is fully customizeable. All fields are printed without an ending newline so that if left blank they will not show. 

    Each item in the menu is represented by a MenuItem. 

    Attributes:  
        sep (str): The seperator between the id and option name.  Default: ". "
        prompt (str): The prompt to ask the user after printing options.  Default: "Type an option: "
        failmsg (str): The message to be displayed if the user provides an invalid option.  Default: "Invalid Option! "
        repeat (bool): If True, repeats the options every prompt. If False, there will be an option to re-show the options. Default False. 
        before (str): The text to be printed before running an option. Default: '\n'
        items (dict): The choice and MenuItem for each item in the menu. 
    """

    def __init__(self, *items, sep=". ", prompt="Type an option: ", failmsg="Invalid Option! ", repeat=False,before='\n'):
        """Inits the object with the given customizations and items.

        Args:
            sep (str): The seperator between the id and option name.  Default: ". "
            prompt (str): The prompt to ask the user after printing options.  Default: "Type an option: "
            failmsg (str): The message to be displayed if the user provides an invalid option.  Default: "Invalid Option! "
            repeat (bool): If True, repeats the options every prompt. If False, there will be an option to re-show the options. Default False. 
            before (str): The text to be printed before exiting an option. Default: '\n'
        """
        self.sep = sep
        self.prompt = prompt
        self.failmsg = failmsg
        self.before = before
        self.repeat = repeat
        self.items = {}
        num = 0
        for i in items:
            if issubclass(i.__class__, MenuItem):
                if i.choice is None:
                    self.items[str(num)] = i
                    num += 1
                else:
                    self.items[i.choice] = i
        if self.repeat:
            self.items.append(CallbackMenuItem('Show these options again', self._show_options))

    def _show_options(self):
        """Formats the items in the menu. """
        for choice, item in self.items.items():
            print(f'{choice}{self.sep}{item.desc}')

    def _get_input(self):
        """
        Gets the choice from the user. 

        Can be overrided in a subclass if you want to do additional processing/stripping. 
        """
        return input(self.prompt)

    def _on_show(self):
        pass

    def _on_run(self):
        print(self.before, end='')

    def show(self, loop_on_incorrect=True):
        """Displays the menu.  
        Returns the item selected and executes it's run() method if it has one. 
        """
        first = True
        self._on_show()
        if self.items == []:
            raise EmptyDataException('Data is empty')
            return
        while first or loop_on_incorrect:
            self._show_options()
            inp = self._get_input()
            if inp not in self.items.keys():
                print(self.failmsg)
                continue
            else:
                item = self.items[inp]
                self._on_run()
                if hasattr(item, 'run'):
                    item.run()
                return item


