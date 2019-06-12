# -*- coding: utf-8 -*-
import contextlib
import os
import re
import shutil
import textwrap

import click

# The trick where we squash multiple spaces into one optimizes for readability.
# It shows the control flow, while keeping the actual shell code to one line
# (important for ease-of-RC-file-management).
_SOURCE_LINE_SH = ' '.join(filter(None, """\
if [ -f '{rc_path}' ]; then \
    source '{rc_path}'; \
fi
""".split(' ')))
_SOURCE_LINE_FISH = ' '.join(filter(None, """\
if [ -f '{rc_path}' ]; \
    if type source > /dev/null; \
       source '{rc_path}'; \
    else; \
       . '{rc_path}'; \
    end; \
end
""".split(' ')))


def _get_rc_contents(comment, rc_path, rc_contents, pattern=None, source_line=_SOURCE_LINE_SH):
    """Generates the RC file contents with new comment and `source rc_path` lines.

    Args:
      comment: The shell comment string that precedes the source line.
      rc_path: The path of the rc file to source.
      rc_contents: The current contents.
      pattern: A regex pattern that matches comment, None for exact match on
        comment.
      source_line: str, the template for sourcing a file in the shell being
        updated ('{rc_path}' will be substituted with the file to source)

    Returns:
      The comment and `source rc_path` lines to be inserted into a shell rc file.
    """
    if not pattern:
        pattern = re.escape(comment)
    # This pattern handles all three variants that we have injected in user RC
    # files. All have the same sentinel comment line followed by:
    #   1. a single 'source ...' line
    #   2. a 3 line if-fi (a bug because this pattern was previously incorrect)
    #   3. finally a single if-fi line.
    # If you touch this code ONLY INJECT ONE LINE AFTER THE SENTINEL COMMENT LINE.
    #
    # At some point we can drop the alternate patterns and only search for the
    # sentinel comment line and assume the next line is ours too (that was the
    # original intent before the 3-line form was added).
    subre = re.compile(
        '\n' + pattern + '\n('
                         "source '.*'"
                         '|'
                         'if .*; then\n  source .*\nfi'
                         '|'
                         'if .*; then source .*; fi'
                         '|'
                         'if .*; if type source .*; end'
                         ')\n', re.MULTILINE)

    # script checks that the rc_path currently exists before sourcing the file
    line = ('\n{comment}\n' + source_line).format(comment=comment, rc_path=rc_path)
    filtered_contents = subre.sub('', rc_contents)
    rc_contents = '{filtered_contents}{line}'.format(filtered_contents=filtered_contents, line=line)

    return rc_contents


TEXTWRAP = textwrap.TextWrapper(replace_whitespace=False,
                                drop_whitespace=False,
                                break_on_hyphens=False)


@contextlib.contextmanager
def _narrow_wrap(narrow_by):
    """Temporarily narrows the global wrapper."""
    TEXTWRAP.width -= narrow_by
    yield TEXTWRAP
    TEXTWRAP.width += narrow_by


def format_required_user_action(s):
    """Formats an action a user must initiate to complete a command.

    Some actions can't be prompted or initiated by gcloud itself, but they must
    be completed to accomplish the task requested of gcloud; the canonical example
    is that after installation or update, the user must restart their shell for
    all aspects of the update to take effect. Unlike most console output, such
    instructions need to be highlighted in some way. Using this function ensures
    that all such instances are highlighted the *same* way.

    Args:
      s: str, The message to format. It shouldn't begin or end with newlines.

    Returns:
      str, The formatted message. This should be printed starting on its own
        line, and followed by a newline.
    """
    with _narrow_wrap(4) as wrapper:
        return '\n==> ' + '\n==> '.join(wrapper.wrap(s)) + '\n'


class RcUpdater(object):
    """Updates the RC file completion and PATH code injection."""

    def __init__(self, shell, completion_path, rc_path):
        self.rc_path = rc_path
        self.completion = completion_path
        self.shell = shell

    def _CompletionExists(self):
        return os.path.exists(self.completion)

    def _GetSourceLine(self):
        if self.shell == 'fish':
            return _SOURCE_LINE_FISH
        else:
            return _SOURCE_LINE_SH

    def update(self):
        #  Check whether RC file is a file and store its contents.
        if os.path.isfile(self.rc_path):
            with open(self.rc_path) as rc_file:
                rc_contents = rc_file.read()
                original_rc_contents = rc_contents
        elif os.path.exists(self.rc_path):
            click.echo(
                '[{rc_path}] exists and is not a file, so it cannot be updated.'.format(rc_path=self.rc_path),
                err=True)
            return
        else:
            rc_contents = ''
            original_rc_contents = ''

        if self._CompletionExists():
            rc_contents = _get_rc_contents(
                '# The next line enables shell command completion for ml (MissingLink.AI command line).',
                self.completion, rc_contents, source_line=self._GetSourceLine(),
                pattern=('# The next line enables [a-z][a-z]*'
                         ' command completion for ml (MissingLink.AI command line).'))

        if rc_contents == original_rc_contents:
            click.echo('No changes necessary for [{rc}].'.format(rc=self.rc_path))
            return

        if os.path.exists(self.rc_path):
            rc_backup = self.rc_path + '.backup'
            click.echo('Backing up [{rc}] to [{backup}].'.format(rc=self.rc_path, backup=rc_backup))
            shutil.copyfile(self.rc_path, rc_backup)

        with open(self.rc_path, 'w') as rc_file:
            rc_file.write(rc_contents)

        click.echo('[{rc_path}] has been updated.'.format(rc_path=self.rc_path))
        click.echo(format_required_user_action('Start a new shell for the changes to take effect.'))


def __get_shell_rc_file_name_from_shell(shell):
    if shell == 'ksh':
        return os.environ.get('ENV', None) or '.kshrc'

    if shell == 'fish':
        return os.path.join('.config', 'fish', 'config.fish')

    if shell != 'bash':
        return '.{shell}rc'.format(shell=shell)

    return None


def __get_shell_rc_file_name_from_platform():
    from sys import platform

    if platform == "linux" or platform == "linux2":
        return '.bashrc'

    if platform == "darwin":
        return '.bash_profile'

    if platform == "win32":
        return '.profile'

    return '.bashrc'


def _get_shell_rc_file_name(shell):
    rc_name = __get_shell_rc_file_name_from_shell(shell)

    if rc_name is None:
        rc_name = __get_shell_rc_file_name_from_platform()

    return rc_name


def rc_updater(shell, completion_path):
    rc_path = os.path.join(os.path.expanduser('~'), _get_shell_rc_file_name(shell))

    # Check the rc_path for a better hint at the user preferred shell.
    RcUpdater(shell, completion_path, rc_path).update()
