# Copyright (C) Bouvet ASA - All Rights Reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.
from ..utils import print_item, exit_with_error, print_message

from ...exceptions import PumpIsAlreadyRunning


def get_pipe_and_exit_if_missing(connection, args):
    pipe = connection.get_pipe(args.pipe_id)
    if pipe is None:
        exit_with_error("No pipe with id '%s' was found!" % (args.pipe_id,))
    return pipe


def get_pump_cmd(connection, args):
    pipe = get_pipe_and_exit_if_missing(connection, args)
    pump = pipe.get_pump()
    print_item(pump, args)


def start_pump_cmd(connection, args):
    pipe = get_pipe_and_exit_if_missing(connection, args)

    pump = pipe.get_pump()
    try:
        pump.start(dont_wait_for_pump_to_start=args.dont_wait_for_pump_to_start)
    except PumpIsAlreadyRunning:
        if not args.allow_already_running_pump:
            exit_with_error("The pump of the pipe id '%s' is already running!" % (args.pipe_id,))

    if args.wait_timeout > 0:
        pump.wait_for_pump_to_finish_running(timeout=args.wait_timeout)

    if args.out in ("json", "yaml"):
        print_item(pump, args)

    elif args.out == "plain":
        print_message("Started the pump in this pipe:")
        print_message(str(pipe))
        print_message("=>", indent=2)
        print_message(str(pump), indent=4)

    else:
        raise NotImplementedError("Output format '%s' has not been implemented!" % (args.out,))


def stop_pump_cmd(connection, args):
    pipe = get_pipe_and_exit_if_missing(connection, args)

    pump = pipe.get_pump()

    pump.stop()

    if args.out in ("json", "yaml"):
        print_item(pump, args)

    elif args.out == "plain":
        print_message("Stopped this  pump:")
        print_message(str(pump))

    else:
        raise NotImplementedError("Output format '%s' has not been implemented!" % (args.out,))


def disable_pump_cmd(connection, args):
    pipe = get_pipe_and_exit_if_missing(connection, args)

    pump = pipe.get_pump()
    pump.disable()

    if args.out in ("json", "yaml"):
        print_item(pump, args)

    elif args.out == "plain":
        print_message("Disabled this pump:")
        print_message(str(pump))

    else:
        raise NotImplementedError("Output format '%s' has not been implemented!" % (args.out,))


def enable_pump_cmd(connection, args):
    pipe = get_pipe_and_exit_if_missing(connection, args)

    pump = pipe.get_pump()
    pump.enable()
    if args.out in ("json", "yaml"):
        print_item(pump, args)

    elif args.out == "plain":
        print_message("Enabled this pipe:")
        print_message(str(pipe))

    else:
        raise NotImplementedError("Output format '%s' has not been implemented!" % (args.out,))


def wait_for_pump_to_finish_running_cmd(connection, args):
    pipe = get_pipe_and_exit_if_missing(connection, args)
    pump = pipe.get_pump()
    pump.wait_for_pump_to_finish_running(timeout=args.timeout)

    if args.out in ("json", "yaml"):
        print_item(pump, args)

    elif args.out == "plain":
        print_message("Waited for this pipe:")
        print_message(str(pipe))

    else:
        raise NotImplementedError("Output format '%s' has not been implemented!" % (args.out,))


def unset_last_seen_cmd(connection, args):
    pipe = get_pipe_and_exit_if_missing(connection, args)

    pump = pipe.get_pump()
    pump.unset_last_seen()
    if args.out in ("json", "yaml"):
        print_item(pump, args)
    elif args.out == "plain":
        print_message("Updated this pump:")
        print_message(str(pump))
    else:
        raise NotImplementedError("Output format '%s' has not been implemented!" % (args.out,))


def update_last_seen_cmd(connection, args):
    pipe = get_pipe_and_exit_if_missing(connection, args)

    pump = pipe.get_pump()
    pump.update_last_seen(args.last_seen)
    if args.out in ("json", "yaml"):
        print_message(pump.as_json())
    elif args.out == "plain":
        print_message("Updated this pump:")
        print_message(str(pump))
    else:
        raise NotImplementedError("Output format '%s' has not been implemented!" % (args.out,))


def run_pump_operation_cmd(connection, args):
    pipe = get_pipe_and_exit_if_missing(connection, args)

    pump = pipe.get_pump()
    operation_parameters_list = args.operation_parameters
    operation_parameters = {}

    def strip_and_remove_enclosing_quotes(value):
        value = value.strip()
        if (value.startswith("'") and value.endswith("'")) or (value.startswith('"') and value.endswith('"')):
            value = value[1:-1]
            value = value.strip()
        return value

    if operation_parameters_list:
        for operation_parameter in operation_parameters_list:
            parameter_name, parameter_value = operation_parameter.split("=", 1)
            parameter_name = strip_and_remove_enclosing_quotes(parameter_name)
            parameter_value = strip_and_remove_enclosing_quotes(parameter_value)
            operation_parameters[parameter_name] = parameter_value

    pump.run_operation(args.operation, operation_parameters)
    if args.out in ("json", "yaml"):
        print_message(pump.as_json())
    elif args.out == "plain":
        print_message("Updated this pump:")
        print_message(str(pump))
    else:
        raise NotImplementedError("Output format '%s' has not been implemented!" % (args.out,))
