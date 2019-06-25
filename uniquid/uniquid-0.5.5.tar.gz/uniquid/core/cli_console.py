# Copyright (c) 2018. Uniquid Inc. or its affiliates. All Rights Reserved.
#
# License is in the "LICENSE" file accompanying this file.
# See the License for the specific language governing permissions and limitations under the License.

import json
import datetime
import os
import sys
import uniquid.core.constants as cons

# constants
_TAB = cons.TXT_TAB


class CliConsole:
    """Generic object which controls all interactions with the command line and
    the console. Independant of the framework which the tool is built with.
    """

    def __init__(self,
                 in_ok=None,
                 in_error=None,
                 in_output=cons.FORMAT_TEXT,
                 in_exc_ctor=RuntimeError,
                 in_confirm=None,
                 in_prompt=None):
        """Create a CliConsole object and store the references to the
           platform specific functions.

           Args:
           in_ok -- Framework function to print strings to console.
           in_error -- Framework function to print errors to the console.
           in_output -- Format of output to terminal.
           in_exc_ctor -- Reference to contructor function to create
           exceptions which should be thrown for the framework.
           in_confirm -- Framework function to query user for yes/no.
           in_prompt -- Framework function to get user input.
        """
        assert in_ok != None
        assert in_confirm != None
        assert in_prompt != None
        assert in_output != None
        assert in_exc_ctor != None
        self._print_ok = in_ok
        self._print_error = None
        self._raise_exception = None
        self._confirm = in_confirm
        self._prompt = in_prompt
        self._format = in_output
        self.is_list_mode = False
        self.num_prints = 0
        self.log = []
        self.timestamp = datetime.datetime.now()
        self.savecwd = os.getcwd()
        if in_error is not None:
            self._print_error = in_error
        elif in_ok is not None:
            self._print_error = in_ok
        self._excp_ctor = in_exc_ctor
        # add the command and arguments to the start of the log
        self.print_log(os.linesep + '(command) ' + ' '.join(sys.argv))

    def ok(self, in_string):
        """Print a string using the pre-configured print function.
            Args:
            in_string -- String to print.
        """
        self.print_log('(OK) ' + in_string)
        self.nolog(in_string=in_string)

    def nolog(self, in_string):
        """Print a string to the console but not the log.
            Args:
            in_string -- String to print.
        """
        if self._print_ok is None:
            self.exception('Print function not assigned.')
        if (self._format == cons.FORMAT_TEXT):
            self._print_ok(in_string)
        elif (self._format == cons.FORMAT_JSON):
            if (self.is_list_mode and
                    self.num_prints > 0):
                self._print_ok(',')
            self._print_ok('{"message": "' + in_string + '"}')
        else:
            self.exception('Internal error: Unexpected format type')
        self.num_prints = self.num_prints + 1

    def error(self, in_string):
        """Print a string using the pre-configured print function.
            Args:
            in_string -- Error message to print."""
        self.print_log('(Error) ' + in_string)
        if self._print_error is None:
            self.exception('Print error function not assigned.')
        if (self._format == cons.FORMAT_TEXT):
            self._print_error('Error: ' + in_string)
        elif (self._format == cons.FORMAT_JSON):
            if (self.is_list_mode and
                    self.num_prints > 0):
                self._print_ok(',')
            self._print_error('{"error": "' + in_string + '"}')
        else:
            self.exception('Internal error: Unexpected format type')
        self.num_prints = self.num_prints + 1

    def exception(self, in_string):
        """Throw an exception which contains the message.
            Args:
            in_string -- Error message to print before exiting."""
        self.print_log('(Exception) ' + in_string)
        self._save_log()
        raise self._excp_ctor(in_string)

    def confirm(self, in_message, in_default=False):
        """
        Ask the user to enter Yes or No.

        Args:
        in_message -- Question put to the user.
        in_default -- True for default Yes if return pressed, otherwise False
        for No.
        Returns:
        True if the user entered Yes, otherwise False.
        """
        assert self._confirm != None
        self.print_log('(Confirm) ' + in_message)
        self.print_log('    default: ' + str(in_default))
        return self._confirm(in_message, default=in_default, show_default=True)

    def prompt(self, in_message, in_type=str, in_default='',
               in_show_default=False):
        """
        Query the user to input a string.

        Args:
        in_message -- Question for user.
        in_type -- Data type of return.
        in_default -- Default response of the user.
        in_show_default -- Display the default value.
        Returns:
        A string entered by the user.
        """
        assert self._prompt != None
        self.print_log('(Prompt) ' + in_message)
        if in_show_default:
            self.print_log('    default: ' + in_default)
        return self._prompt(in_message, type=in_type,
                            default=in_default, show_default=in_show_default)

    def checkpoint(self):
        """Inform the CliConsole that the log file should be updated.
        """
        self._save_log()

    def happy_exit(self):
        """Inform the CliConsole that the application is about to exit.
            The log should also be saved before exiting and any other cleanup
            performed.
        """
        self._save_log()

    def begin_list(self):
        """Print prefix lines to all text output for the command.

        Places the object in List mode, which means it expects to print
        multiple data objects to the CLI."""
        if self._print_ok is None:
            self.exception('Print function not assigned.')
        if self._format == cons.FORMAT_JSON:
            self._print_ok('[')
            self.print_log('[')
        self.is_list_mode = True

    def end_list(self):
        """Print suffix lines to all text output for the command."""
        if self._print_ok is None:
            self.exception('Print function not assigned.')
        if self._format == cons.FORMAT_JSON:
            self._print_ok(']')
            self.print_log(']')
        self.is_list_mode = False
        self.num_prints = 0

    def print_objects(self, in_objs, in_is_vertical=False):
        """Print object(s) to the console in the requested format.

        Args:
        in_objs -- A Python object. May be a dictionary or a list.
        in_is_vertical -- If true, force printing of multiple objects in a
        vertical direction i.e. one key and value per line rather than
        tabulated data in a horizontal direction. False indicates that
        data should be tabulated in a horizontal direction.
        Argument only affects text output. Has no effect on JSON output.
        """
        if self._format == cons.FORMAT_JSON:
            if (self.is_list_mode and
                    self.num_prints > 0):
                self._print_ok(',')
                self.print_log(',')
            self._print_ok(json.dumps(in_objs,
                                      sort_keys=False,
                                      indent=4))
            self.print_log(str(in_objs))
        elif self._format == cons.FORMAT_TEXT:
            if (isinstance(in_objs, list)
                    and in_is_vertical == False):
                self._print_list_horiz(in_objs)
            elif isinstance(in_objs, list):
                self._print_list_vert(in_objs)
            elif (isinstance(in_objs, dict)
                    and in_is_vertical == False):
                self._print_dict_horiz(in_objs)
            elif isinstance(in_objs, dict):
                self._print_dict_vert(in_objs)
            else:
                self.exception('Internal: Unsupported object type: '
                               + str(type(in_objs)))
        else:
            self.exception('Internal: Unsupported text format.')
        self.num_prints = self.num_prints + 1

    def print_log(self, in_string):
        """Append a string to the log list. Adds a timestamp before the string
            and clears the log entry cache. Can be used to add information
            to the log which isn't printed to the console.
            Args:
            in_string -- String to add to the log.
        """
        timenow = self.timestamp.strftime('[%d/%m/%Y %H:%M:%S] ')
        self.log.append(timenow + in_string)

    def _print_list_horiz(self, in_list):
        """Print a list of objects in horizontal table.

            Args:
            in_list -- List of objects."""
        assert isinstance(in_list, list)
        # print the header from the first object in the list
        if (len(in_list) > 0 and
                isinstance(in_list[0], dict)):
            key_list = self._get_hier_keys(in_list[0])
            self._print_ok(_TAB.join(key_list).upper())
            self.print_log(_TAB.join(key_list).upper())
        # print rows for all objects in the list
        for obj in in_list:
            self._print_ok(_TAB.join(self._get_hier_values(obj)))
            self.print_log(_TAB.join(self._get_hier_values(obj)))
        return

    def _print_list_vert(self, in_list):
        """Print a list of objects vertically i.e. a new line per item.

            Args:
            in_list -- List of objects."""
        assert isinstance(in_list, list)
        # print a line for each object in the list
        for obj in in_list:
            if isinstance(obj, dict):
                self._print_dict_vert(dict)
            elif isinstance(obj, list):
                self._print_list_vert(obj)
            else:
                self.exception('Internal: Unsupported object type in list.')

    def _print_dict_vert(self, in_dict):
        """Print a dictionary vertically i.e. one line per key.

            Args:
            in_dict -- Dictionary object."""
        assert isinstance(in_dict, dict)
        for k, v in in_dict.items():
            self._print_ok(_TAB.join([str(k).upper(), str(v)]))
            self.print_log(_TAB.join([str(k).upper(), str(v)]))
        return

    def _print_dict_horiz(self, in_dict):
        """Print a dictionary in a horizontal table.

            Args:
            in_dict -- Dictionary object."""
        # print the header from the object
        self._print_ok(_TAB.join(self._get_hier_keys(in_dict)).upper())
        self.print_log(_TAB.join(self._get_hier_keys(in_dict)).upper())
        # print row with values from object
        self._print_ok(_TAB.join(self._get_hier_values(in_dict)))
        self.print_log(_TAB.join(self._get_hier_values(in_dict)))
        return

    def _get_hier_keys(self, in_objs):
        """Get a list of all of the keys in the object hierarchy."""
        retval = list()
        if isinstance(in_objs, list):
            for item in in_objs:
                list_keys = self._get_hier_keys(item)
                retval.extend(list_keys)
        elif isinstance(in_objs, dict):
            for key, value in in_objs.items():
                if (isinstance(value, dict) or
                        isinstance(value, list)):
                    sub_keys = self._get_hier_keys(value)
                    if len(sub_keys) > 0:
                        for sub_key in sub_keys:
                            retval.append(str(key) + '_' + str(sub_key))
                    else:
                        retval.append(str(key))
                else:
                    retval.append(str(key))
        return retval

    def _get_hier_values(self, in_objs):
        """Get a list of all of the values in the object hierarchy."""
        retval = list()
        if isinstance(in_objs, list):
            aglom = list()
            aglom.append('[')
            for item in in_objs:
                list_values = self._get_hier_values(item)
                for value in list_values:
                    aglom.append(str(value))
                if item is not in_objs[-1]:
                    aglom.append(',')
            aglom.append(']')
            retval.append(''.join(aglom))
        elif isinstance(in_objs, dict):
            for item in in_objs.values():
                dict_values = self._get_hier_values(item)
                for item in dict_values:
                    retval.append(str(item))
        else:
            retval.append(str(in_objs))
        return retval

    def _save_log(self):
        """Write log entries to a file in the machine's current working
           directory.
        """
        day = self.timestamp.strftime('%Y%m%d')
        log_name = cons.LOG_PREFIX + day + cons.LOG_SUFFIX
        log_path = os.path.join(self.savecwd,
                                log_name)
        with open(log_path, 'a') as f:
            for entry in self.log:
                print(entry, file=f)
        self.log.clear()
