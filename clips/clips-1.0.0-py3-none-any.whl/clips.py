from collections import namedtuple
from sys import exit as sys_exit
import getopt

__all__ = ['ArgParser']
__version__ = '1.0.0'

# base-section
BASE = 'BASE'

# color sequences
foreground_colors = {
    'black': '\033[30m', 'red': '\033[31m', 'green': '\033[32m',
    'orange': '\033[33m', 'blue': '\033[34m', 'purple': '\033[35m',
    'cyan': '\033[36m', 'lightgrey': '\033[37m', 'darkgrey': '\033[90m',
    'lightred': '\033[91m', 'lightgreen': '\033[92m', 'yellow': '\033[93m',
    'lightblue': '\033[94m', 'pink': '\033[95m', 'lightcyan': '\033[96m'
}

background_colors = {
    'black': '\033[40m', 'red': '\033[41m', 'green': '\033[42m',
    'orange': '\033[43m', 'blue': '\033[44m', 'purple': '\033[45m',
    'cyan': '\033[46m', 'lightgrey': '\033[47m'
}

class ClipsError(Exception):
    """ Simple exception wrapper. """

class TextColor:
    """ Class for coloring text. """
    def __init__(self, fg=None, bg=None):
        # set foreground
        if fg:
            if fg not in foreground_colors.keys():
                raise ClipsError('Foreground color not suported')
            color_fg = foreground_colors[fg]
        else:
            color_fg = ''
        # set background
        if bg:
            if bg not in background_colors.keys():
                raise ClipsError('Background color not supported')
            color_bg = background_colors[bg]
        else:
            color_bg = ''
        self.prefix = color_bg+color_fg
        self.reset = '\033[0m' if (fg or bg) else ''

    def render(self, text):
        """ Display text with selected colors. """
        return '{0}{1}{2}'.format(self.prefix, text, self.reset)

class UsageFormatter:
    """ Formatter for usage messages. """
    def __init__(self,name,description=None,banner=None,title_fg=None,
        title_bg=None,text_fg=None,text_bg=None,indent=[0]):
        self.name = name
        self._description = description
        self._banner = banner
        self._title_color = TextColor(fg=title_fg,bg=title_bg)
        self._text_color= TextColor(fg=text_fg,bg=text_bg)
        self.indent = indent

    def _usage_string(self,obj,args,opts):
        """ Prepare usage string. """
        usage_string = 'usage: '+self.name+' '
        usage_string += ''.join([cmd+' ' for cmd in obj.chain[1:]])
        if obj._commands: usage_string += '[command] '
        if args: usage_string += ' '.join([str(arg) for arg in args])+' '
        if opts: usage_string += '[options]'
        return usage_string

    def _group_usage(self,usage_help,title,commands):
        """ Render the command usage. """
        title_color = self._title_color
        text_color = self._text_color
        off = 4+self.indent[0]

        usage_help += '\n' + ' '*2 + title_color.render(title)+'\n'
        usage_help += '\n'.join([
            ' '*4 + text_color.render(str(c)) +
            ' '*(off-len(str(c))) +
            (c.help or '')
            for c in commands])
        return usage_help

    def get_usage_help(self,obj):
        """ Print general help message. """
        title_color = self._title_color
        text_color = self._text_color
        off = 4+self.indent[0]

        # prepare usage string
        usage_help = ''
        if self._banner: usage_help += text_color.render(self._banner)+'\n'
        if self._description: usage_help += self._description+'\n'

        # unpack positional args and options
        opts = []
        args = []
        for _arg in obj._args:
            args.append(_arg) if isinstance(_arg,Positional) else opts.append(_arg)

        # add usage string
        usage_help += '\n'+self._usage_string(obj,args,opts)+'\n'

        # format commands
        commands = obj._commands
        if commands:
            if len(obj.chain)==1 and obj.sections:

                printed = []
                # section commands
                for section,command_names in obj.sections.items():

                    section_commands = [c for c in commands if c.name in command_names]
                    printed += section_commands

                    usage_help = self._group_usage(usage_help,section,section_commands)

                # other commands
                others = set(commands).difference(set(printed))
                if others:
                    usage_help = self._group_usage(usage_help,'Other:',others)

            else:
                usage_help = self._group_usage(usage_help,'Commands',commands)

            usage_help+='\n'

        # format options
        if opts:
            usage_help = self._group_usage(usage_help,'Options',opts)
            usage_help+='\n'

        # format arguments
        if args:
            usage_help = self._group_usage(usage_help,'Arguments',args)
            usage_help+='\n'

        return usage_help

class Positional:
    """ Class for positional arguments. """
    __slots__=('name','help')
    def __init__(self,name,help=None):
        self.name=name
        self.help=help

    def get_names(self):
        return [self.name]

    def __str__(self):
        return self.name

class Optional:
    """ Class for optional arguments. """
    __slots__=('short','long','s_repr','l_repr','valued','help')
    def __init__(self,short=None,long=None,s_repr='',l_repr='',valued=False,help=None):
        self.short=short
        self.long=long
        self.s_repr=s_repr
        self.l_repr=l_repr
        self.valued=valued
        self.help=help

    def get_names(self):
        return [name for name in [self.short,self.long] if name]

    def __str__(self):
        if self.short and self.long:
            s = ','.join([self.short,self.long])
        else:
            s = self.short or self.long
        return s

class BaseCommand:
    """ The base command class. Provides API for adding subcommands
    and arguments. """

    def __init__(self,chain,context,indent,help=None,add_help=True):
        self.chain = chain
        self.context = context
        self.indent=indent
        self.help = help
        self._commands = []
        self._args = []

        if add_help:
            self.add_argument('-h','--help',help='Show this messsage and exit.')

    def add_command(self,name,help=None):
        """ Add a chained sub-command. """
        # update context, chain, indent
        chain = self.chain+[name]
        self.indent[0] = max(self.indent[0],len(chain[-1]))
        self.context[name]=False
        # create new command
        command = Command(chain,self.context,self.indent,help=help)
        self._commands.append(command)
        return command

    def add_argument(self,*arg,valued=False,help=None):
        """ Add a command argument. """
        token = self._parse_arg(arg,valued,help)
        for name in token.get_names():
            self.context[name]=False
        self._args.append(token)
        self.indent[0] = max(self.indent[0],len(str(arg)))
        return

    def _parse_arg(self,arg,valued=False,help=None):
        """ Parse argument with getopt formatting style. """
        s_opt=''
        l_opt=''
        short=None
        long=None
        for el in arg:
            if el.startswith('-'):
                # long-option
                if el.startswith('--'):
                    long = el
                    l_opt = el[2:]
                    if valued: l_opt+='='
                # short-option
                else:
                    short = el
                    s_opt = el[1:]
                    if valued: s_opt+=':'
            else:
                return Positional(el,help)
        return Optional(short,long,s_opt,l_opt,valued,help)


class Command(BaseCommand):
    """ Class for chainable command with arguments. """

    @property
    def name(self):
        return self.chain[-1]

    def __str__(self):
        return self.chain[-1]

class ArgParser(BaseCommand):
    """ Main class for CLI. Commands can be grouped by sections and
    chained together. Arguments can be positional or optional (flags)."""

    def __init__(self,name,banner=None,description=None,add_help=True,
        title_fg=None,title_bg=None,text_fg=None,text_bg=None):

        self.name = name
        self._add_help = add_help
        self.sections = {}
        self.curr_section=None

        # text indentation
        indent = [0]

        # init usage formatter
        self.usage_formatter = UsageFormatter(name,description=description,
            banner=banner,title_fg=title_fg,title_bg=title_bg,
            text_fg=text_fg,text_bg=text_bg,indent=indent)

        super().__init__([BASE],{},indent,help=help,add_help=add_help)

    def add_section(self,name):
        """ Add a section for next commands. """
        self.sections[name] = []
        self.curr_section=name

    def add_command(self,name,help=None):
        """ Add a new subcommand. """
        if self.curr_section:
            self.sections[self.curr_section].append(name)
        return super().add_command(name,help=help)

    def parse_args(self,args):
        """ Parse commands and arguments and returns the user context. """
        assert isinstance(args,list)

        obj,context = self._strip_args(args)

        # command arguments
        cmd_args = [tok.name for tok in obj._args if isinstance(tok,Positional)]

        # prepare getopt
        options = [tok for tok in obj._args if isinstance(tok,Optional)]
        shortopts = ''.join([opt.s_repr for opt in options])
        longopts = [opt.l_repr for opt in options]

        # parse arguments
        try:
            optlist,args = getopt.gnu_getopt(args,shortopts,longopts)
        except getopt.GetoptError as ge:
            raise ClipsError(str(ge))

        # flag options
        for opt in optlist:
            if opt[1]:
                context[opt[0]]=opt[1]
            else:
                context[opt[0]]=True

        # help hook
        if self._add_help and (context['-h'] or context['--help']):
            print(self.usage_formatter.get_usage_help(obj))
            sys_exit()

        # arg checking
        num_passed_args = len(args)
        num_cmd_args = len(cmd_args)
        if num_passed_args==num_cmd_args:
            # assign arguments
            for ii,cmd_arg in enumerate(cmd_args):
                context[cmd_arg]=args[ii]
        elif num_cmd_args>num_passed_args:
            raise ClipsError('Missing required argument: \'{0}\''.format(cmd_args[num_passed_args]))
        else:
            raise ClipsError('Unknown argument: \'{0}\''.format(args[num_cmd_args]))

        return context

    def _strip_args(self,args):

        context = self.context.copy()

        obj=self
        chain = [BASE]

        command_names = [cmd.name for cmd in self._commands]
        while args and command_names and args[0] in command_names:
            # strip command
            arg=args.pop(0)
            context[arg]=True
            obj=obj._commands[command_names.index(arg)]
            commands = obj._commands
            command_names = [cmd.name for cmd in commands]
            chain.append(arg)

        return obj,context

    def usage_help(self,args=[]):

        obj,_ = self._strip_args(args)
        return self.usage_formatter.get_usage_help(obj)
