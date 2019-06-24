"""This is the external interface to the Rook package."""
import sys
import os
import traceback
import re

import six

from rook.config import ImportServiceConfig

_rook = None
_debug = False
_throw_errors = False

_TRUE_VALUES = ['y', 'Y', 'yes',  'Yes',  'YES', 'true', 'True', 'TRUE', '1', True]


def start(token=None,
          tags=None,
          host=None,
          port=None,
          debug=None,
          throw_errors=None,
          log_file=None,
          log_level=None,
          log_to_stderr=None,
          labels=None,
          use_import_hook=None,
          git_commit=None,
          git_origin=None,
          **kwargs):
    global _rook, _debug, _throw_errors

    if _rook is not None:
        return

    if isinstance(debug, bool):
        _debug = debug
    else:
        _debug = os.environ.get('ROOKOUT_DEBUG') in _TRUE_VALUES

    if isinstance(log_to_stderr, bool):
        log_to_stderr = log_to_stderr
    else:
        log_to_stderr = os.environ.get('ROOKOUT_LOG_TO_STDERR') in _TRUE_VALUES

    if isinstance(throw_errors, bool):
        _throw_errors = throw_errors

    if not isinstance(tags, list) and isinstance(os.environ.get('ROOKOUT_ROOK_TAGS'), six.string_types):
        raw_tags = os.environ.get('ROOKOUT_ROOK_TAGS')
        tags = [_normalize_string(tag.strip()) for tag in raw_tags.split(';') if tag]

    if not isinstance(labels, dict) and isinstance(os.environ.get('ROOKOUT_LABELS'), six.string_types):
        raw_labels = os.environ.get('ROOKOUT_LABELS')
        labels = {}
        for label in raw_labels.split(','):
            label = _normalize_string(label.strip())
            keyvalue = label.split(':')
            if len(keyvalue) == 2:
                key,value = keyvalue
                if key and value:
                    _validate_label(key)
                    labels[key] = value

    log_file = log_file or os.environ.get('ROOKOUT_LOG_FILE')
    log_level = log_level or os.environ.get('ROOKOUT_LOG_LEVEL')
    host = host or os.environ.get('ROOKOUT_CONTROLLER_HOST') or os.environ.get('ROOKOUT_AGENT_HOST')
    port = port or os.environ.get('ROOKOUT_CONTROLLER_PORT') or os.environ.get('ROOKOUT_AGENT_PORT')
    token = token or os.environ.get('ROOKOUT_TOKEN')
    use_import_hook = use_import_hook if use_import_hook is not None else os.environ.get('ROOKOUT_USE_IMPORT_HOOK',
                                                                                         False) in _TRUE_VALUES
    async_start = os.environ.get('ROOKOUT_ASYNC_START', False) in _TRUE_VALUES

    try:
        from rook.exceptions.tool_exceptions import RookMissingToken, RookInvalidToken, RookVersionNotSupported, \
            RookCommunicationException, RookInvalidOptions, RookLoadError
        try:
            from rook.config import LoggingConfiguration, GitConfig

            if git_commit is not None:
                if not isinstance(git_commit, six.string_types):
                    raise RookInvalidOptions('Git commit should be a String')
                GitConfig.GIT_COMMIT = git_commit

            if git_origin is not None:
                if not isinstance(git_origin, six.string_types):
                    raise RookInvalidOptions('Git origin should be a String')
                GitConfig.GIT_ORIGIN = git_origin

            if log_file is not None:
                if not isinstance(log_file, six.string_types):
                    raise RookInvalidOptions('Rook log file should be a String')
                LoggingConfiguration.FILE_NAME = log_file

            if log_level is not None:
                if not isinstance(log_level, six.string_types):
                    raise RookInvalidOptions('Rook log level should be a String')
                LoggingConfiguration.LOG_LEVEL = log_level

            if log_to_stderr is not None:
                LoggingConfiguration.LOG_TO_STDERR = log_to_stderr

            if _debug:
                LoggingConfiguration.LOG_LEVEL = 'DEBUG'
                LoggingConfiguration.LOG_TO_STDERR = True
                LoggingConfiguration.DEBUG = True

            if use_import_hook is not None:
                ImportServiceConfig.USE_IMPORT_HOOK = use_import_hook

            if isinstance(tags, list):
                for tag in tags:
                    if not isinstance(tag, six.string_types):
                        raise RookInvalidOptions('Rook tags should be array of strings')
            else:
                if tags:
                    raise RookInvalidOptions('Rook tags should be array of strings')

            if not host and not token:
                raise RookMissingToken()
            else:
                if token is not None:
                    _validate_token(token)

            if (host == "staging.cloud.agent.rookout.com") or (host == "cloud.agent.rookout.com"):
                host = "https://" + host

            if (host == "staging.control.rookout.com") or (host == "control.rookout.com"):
                host = "wss://" + host

            import rook.singleton
            _rook = rook.singleton.singleton_obj

            return _rook.connect(token, host, port, tags, labels, async_start=async_start)
        except (RookMissingToken, RookInvalidToken, RookVersionNotSupported) as e:
            if not _throw_errors:
                six.print_("[Rookout] Failed to start Rookout:", e, file=sys.stderr)
            raise
        except RookCommunicationException:
            if not _throw_errors:
                six.print_("[Rookout] Failed to connect to the agent - will continue attempting in the background", file=sys.stderr)
            raise
        except ImportError as e:
            if not _throw_errors:
                six.print_("[Rookout] Failed to import dependencies:", e, file=sys.stderr)
            raise
        except (Exception, RookLoadError) as e:
            if not _throw_errors:
                six.print_("[Rookout] Failed initialization:", e, file=sys.stderr)
            raise
    except Exception:
        if _throw_errors:
            raise

        if _debug:
            traceback.print_exc()


def flush():
    global _rook
    if _rook is None:
        return

    _rook.flush()


def stop():
    global _rook
    if _rook is None:
        return

    _rook.stop()
    _rook = None


def _normalize_string(obj):
    if six.PY2:
        if isinstance(obj, str):
            return unicode(obj, errors="replace")
        else:
            return unicode(obj)
    else:
        return str(obj)


def _validate_token(token):
    from rook.exceptions import RookInvalidOptions

    if not isinstance(token, six.string_types):
        raise RookInvalidOptions('Rookout token should be a String')

    if len(token) != 64:
        raise RookInvalidOptions('Rookout token should be 64 characters')

    if re.match("^[0-9a-zA-Z]{0,64}$", token) is None:
        raise RookInvalidOptions('Rookout token must consist of only hexadecimal characters')


def _validate_label(label):
    from rook.exceptions import RookInvalidLabel

    if label.startswith("$"):
        raise RookInvalidLabel(label)
