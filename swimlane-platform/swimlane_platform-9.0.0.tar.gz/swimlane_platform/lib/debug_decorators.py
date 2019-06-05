import functools


def info_function_start_finish(action_description=None):

    def wrap(func):
        action = action_description if action_description else func.func_name.replace('_', ' ') + '.'

        @functools.wraps(func)
        def echo_func(*args, **kwargs):
            if args[0] and hasattr(args[0], 'logger'):
                logger = args[0].logger
                logger.info('Starting {action}'.format(action=action))
                result = func(*args, **kwargs)
                logger.info('Finishing {action}'.format(action=action))
                return result
            else:
                return func(*args, **kwargs)

        return echo_func
    return wrap


def debug_function_args(func):
    arg_names = func.func_code.co_varnames[:func.func_code.co_argcount]
    function_name = func.func_name

    @functools.wraps(func)
    def echo_func(*args, **kwargs):
        if args[0] and hasattr(args[0], 'logger'):
            logger = args[0].logger
            names = arg_names[1:]
            values = args[1:]
            asterisk = []
            if len(names) < len(values):
                asterisk = [('*', values[len(names):])]
            args_with_values = ', '.join('%s=%r' % entry for entry in zip(names, values) + asterisk + kwargs.items())
            logger.debug('{name} called with {args}'.format(name=function_name, args=args_with_values))

        return func(*args, **kwargs)

    return echo_func


def debug_function_return(func):
    function_name = func.func_name

    @functools.wraps(func)
    def echo_func(*args, **kwargs):
        if args[0]and hasattr(args[0], 'logger'):
            logger = args[0].logger
            result = func(*args, **kwargs)
            logger.debug('{name} returned {result}'.format(name=function_name, result=result))
            return result
        else:
            return func(*args, **kwargs)

    return echo_func
