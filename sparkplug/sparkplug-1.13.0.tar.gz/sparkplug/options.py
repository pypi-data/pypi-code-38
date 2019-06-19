import pwd
import grp
import copy
import optparse


def check_umask(options, optname, value):
    try:
        # Umasks look like octal.
        return int(value, 8)
    except ValueError:
        raise optparse.OptionValueError(
            "option %s: %r doesn't look like a umask to me, bucko" % (optname, value)
        )


def check_uid(options, optname, value):
    try:
        pw = pwd.getpwuid(int(value))
        return pw.pw_uid
    except (KeyError, ValueError):
        # Either not a valid uid or not an integer. Try it as a username.
        try:
            pw = pwd.getpwnam(value)
            return pw.pw_uid
        except KeyError:
            # Nope, that didn't work either. Die screaming.
            raise optparse.OptionValueError(
                "option %s: %r doesn't look like a valid uid or username from here"
                % (optname, value)
            )


def check_gid(options, optname, value):
    try:
        gr = grp.getgrgid(int(value))
        return gr.gr_gid
    except (KeyError, ValueError):
        # Either not a valid gid or not an integer. Try it as a group name.
        try:
            gr = grp.getgrnam(value)
            return gr.gr_gid
        except KeyError:
            # Nope, that didn't work either. Die screaming.
            raise optparse.OptionValueError(
                "option %s: %r doesn't look like a valid gid or group name from here"
                % (optname, value)
            )


class Option(optparse.Option):
    TYPES = optparse.Option.TYPES + ("umask", "uid", "gid")
    TYPE_CHECKER = copy.copy(optparse.Option.TYPE_CHECKER)
    TYPE_CHECKER["umask"] = check_umask
    TYPE_CHECKER["uid"] = check_uid
    TYPE_CHECKER["gid"] = check_gid
