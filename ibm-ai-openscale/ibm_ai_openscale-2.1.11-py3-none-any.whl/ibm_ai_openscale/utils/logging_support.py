import logging


# TODO add support for staticmethods
# TODO make search in args and results for secret content
def enter(cls, function_name, context=None, args=[], kwargs={}):
    cls._logger.debug(
        'Called {}.{}({}){}'.format(
            cls.__class__.__name__,
            function_name,
            ', '.join(list([arg.__repr__() for arg in args]) + list(
                [str(item[0]) + '=' + item[1].__repr__() for item in kwargs.items()])),
            ', context: ' + ', '.join(
                [str(item[0]) + '=' + item[1].__repr__() for item in context.items()]) if context is not None else ' '
        )
    )


def leave(cls, function_name, context=None, result=None):
    cls._logger.debug(
        'Leaving {}.{}{} function{}'.format(
            cls.__class__.__name__,
            function_name,
            ', context: (' + ', '.join([pair[0] + ': ' + pair[1].__repr__() for pair in context.items()]) + ')' if context is not None else ' ',
            ' with result: {}'.format(result) if result is not None else ''
        )
    )


def logging_func(func):
    if func.__name__ == 'logging_func':
        return func

    #@wraps
    def call(*args, **kwargs):
        self = args[0]
        prepared_args = args[1:]

        def hide_secrets(arg):
            if type(arg) == dict:
                cloned_arg = arg.copy()

                for key in cloned_arg:
                    if 'secret' in key or 'password' in key or 'apikey' in key or 'api_key' in key:
                        cloned_arg[key] = '***'

                return cloned_arg
            else:
                return arg

        prepared_args = [hide_secrets(arg) for arg in prepared_args]
        prepared_kwargs = {key: hide_secrets(kwargs[key]) for key in kwargs}

        context = {}
        if '_subscription' in self.__dict__:
            context['subscription'] = self.__dict__['_subscription']

        if len(context) == 0:
            context = None

        enter(self, func.__name__, context=context, args=prepared_args, kwargs=prepared_kwargs)
        result = func(*args, **kwargs)
        leave(self, func.__name__, context=context, result=result)
        return result
    return call


def logging_class(cls):
    for attr in cls.__dict__:
        func = getattr(cls, attr)
        if callable(attr):
            logging_func = logging_func(func)
            logging_func.__doc__ = attr.__doc__
            setattr(cls, attr, logging_func)

    if '_logger' not in cls.__dict__:
        setattr(cls, '_logger', logging.getLogger(cls.__name__))

    return cls