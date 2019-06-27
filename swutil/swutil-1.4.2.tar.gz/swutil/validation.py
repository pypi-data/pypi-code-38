import six
import ast
import builtins
import numbers
from math import inf
from swutil.decorators import find_implementation, default
import itertools
from _collections import defaultdict
import inspect
import functools
from inspect import signature
from abc import ABC, abstractmethod
import numpy
import timeit
import warnings
import math

# Don't use brackets for subspecifications because of lack of support for keyword arguments
# _validate has to raise error instead of returning None

class ValidationError(Exception):
    pass

class _NotPassed():
    '''
    The instance `NotPassed` defined below may be used to substitute for None as a default argument.
    
    Note that this instance can also be used in functional form to check if an argument was passed:
    def f(a=NotPassed):
        if Passed(a):
            print('Argument passed for parameter `a` was: {}'.format(a))
        if NotPassed(a):
            print('No argument was passed for parameter `a`')
    >>>f(1)
    Argument passed for parameter `a` was: 1
    >>f()
    Parameter `a` was not passed
    '''
    def __bool__(self):
        return False
    def __str__(self):
        return '<NotPassed>'
    def __repr__(self):
        return '<NotPassed>'
    def __eq__(self, other):
        return isinstance(other, _NotPassed)  # Cannot self is other because this will give problems after serializing
    def __req__(self, other):
        return isinstance(other, _NotPassed)
    def valid(self, arg):
        return isinstance(arg, _NotPassed)
    def __call__(self, other):
        return isinstance(other, _NotPassed)
NotPassed = _NotPassed()

#def Passed(arg):
#    return not NotPassed(arg)
class _Passed():
    '''
    
    '''
    @staticmethod
    def valid(arg):
        return not NotPassed(arg)
    @staticmethod
    def __call__(arg):
        return not NotPassed(arg)

Passed = _Passed()

class Specification(ABC):
    '''
    Specifies desired properties of objects.
    
    Instances of subclasses can be passed to `validate`.
    
    Subclasses must implement method `valid` which determines whether all desired properties are satisfied.
    
    Subclasses may define property `lenience` and implement method `forgive`, which
    together allow that objects that are at first not valid are transformed into a validity.  
    
    Subclasses may overwrite `_validate` 
    '''
    def __init__(self, lenience=1):
        if (not isinstance(lenience, (builtins.int, builtins.bool))) or lenience < 0:
            raise TypeError('`lenience` must be a positive integer')  # Can also be bool, but shouldn't
        lenience = int(lenience)
        self.lenience = lenience
    def __call__(self, *args, **kwargs):
        return self.__class__(*args, **kwargs)
    def _validate(self, arg):  # unforgiving version, only to be used by validate (which wraps this in the forgive loop) 
        if self.valid(arg):
            return arg
        else:
            raise ValidationError
    @abstractmethod
    def valid(self, arg):
        pass
    def __gt__(self, other):
        return _Connection(self, other, connective=_implies)
    def __lt__(self, other):
        return _Connection(other, self, connective=_implies)
    def __eq__(self, other):
        return _Connection(self, other, connective=_equal)
    def __xor__(self, other):
        return _Connection(self, other, connective=_xor)
    def __and__(self, other):
        return _Connection(self, other, connective=_and) 
    def __or__(self, other):
        return _Connection(self, other, connective=_or) 
    def __invert__(self):
        return _Inverted(self)
    def __str__(self):
        return self.__class__.__name__
    def __repr__(self):
        return str(self)
    def __format__(self, format_spec):
        return str(self) 
     
class _Inverted(Specification):
    def __init__(self, other):
        self.other = other
    def valid(self, arg):
        return not self.other.valid(arg)
    def __str__(self):
        return '~(' + str(self.other) + ')'
    
def validate(arg, spec):
    '''
    Make sure `arg` adheres to specification
    
    :param arg: Anything
    :param spec: Specification
    :type spec: Specification
    
    :return: Validated object
    '''
    rejection_subreason = None
    if spec is None:
        return arg
    try:
        return spec._validate(arg)
    except Exception as e:
        rejection_subreason = e
    try:
        lenience = spec.lenience
    except AttributeError:
        pass
    else:
        for level in range(1, lenience + 1):
            temp = None
            try:
                temp = spec.forgive(arg=arg, level=level)
            except Exception:
                pass  # Forgiving might fail, it is very hard to predict what happens when you do stuff to things that aren't what you think
            if temp is not None and temp is not arg:
                arg = temp
                try:
                    return spec._validate(arg)
                except Exception as e:
                    rejection_subreason = e
    rejection_reason = '`{}` was rejected by `{}`.'.format(arg, spec)
    rejection_subreason = ' ({}: {})'.format(rejection_subreason.__class__.__name__, rejection_subreason) if rejection_subreason is not None else ''
    raise ValidationError(rejection_reason + rejection_subreason)
    
def _validate_many(args, specs, defaults,passed_conditions,value_conditions,
                  allow_unknowns,unknowns_spec): 
    '''
    Similar to validate but validates multiple objects at once, each with their own specification. 
    
    Fill objects that were specified but not provided with NotPassed or default values
    Apply `value_condition` to object dictionary as a whole 
    '''
    validated_args = builtins.dict() 
    passed_but_not_specified = set(args.keys()) - set(specs.keys())
    if passed_but_not_specified:
        if not allow_unknowns:
            raise ValueError(('Arguments {} were passed but not specified (use ' + 
                 '`allow_unknowns=True` to avoid this error)'.format(passed_but_not_specified)))
        else:
            for arg in passed_but_not_specified:
                if unknowns_spec is not None:
                    specs[arg] = unknowns_spec
    if passed_conditions:
        validate(args, Dict(passed_conditions=passed_conditions))
    for arg in specs:
        if (not arg in args) or NotPassed(args[arg]):
            if arg in defaults:
                if isinstance(defaults[arg],DefaultGenerator):
                    validated_args[arg] = defaults[arg]()
                else:
                    validated_args[arg] = defaults[arg]
            else:
                validated_args[arg] = NotPassed
        else:#Default values and NotPassed values are not validated. Former has advantage that default values need to be `correct` without validation and thus encourage the user to pass stuff that doesn't need validation, and is therefore faster
            validated_args[arg] = validate(args[arg], specs[arg])
    if value_conditions:
        validated_args = validate(validated_args, value_conditions)
    return validated_args

class validate_args():  # DecoratorFactory
    '''
    Provides decorators that make sure arguments passed to functions satisfy 
    Specifications in type hints and the group of arguments as a whole satisfies 
    specifications in parameter `conditions`
    
    Elements of `conditions` can be strings with logical expressions or arbitrary Specifications.
    The former may be used to specify which arguments must be passed. For example,
    the condition 'a>b c^d' means that `b` must be passed whenever `a` is, and 
    exactly one of `c` and `d` must be passed. 
    '''
    def __init__(self, *conditions, allow_unknowns=False,
                 unknowns_specification=NotPassed, warnings=True,deactivate=False):
        self.deactivated= deactivate
        if not self.deactivated:
            unknowns_specification = unknowns_specification or Any
            for condition in conditions:
                if not isinstance(condition, (six.string_types, Specification)):
                    raise TypeError('`conditions` must be strings or instances of `Specification` (failed on {})'.format(condition))
            if not isinstance(allow_unknowns, builtins.bool):
                raise TypeError('`allow_unknowns` must be boolean')
            if not isinstance(unknowns_specification, Specification):
                raise TypeError('`unknowns_specification` must be instance of `Specification`')
            passed = None
            value = None 
            for condition in conditions:
                if isinstance(condition, six.string_types):
                    if passed is None:
                        passed = condition
                    else:
                        passed += ' ' + condition
                elif isinstance(condition, Specification):
                    if value is None:
                        value = condition
                    else:
                        value = value & condition 
            self.passed = passed
            self.value = value
            self.allow_unknowns = allow_unknowns
            self.unknowns_specification = unknowns_specification 
            self.warnings = warnings
        
    def __call__(self, f):
        if self.deactivated:
            return f
        else:
            return _ValidatedInputFunction(f, self.passed, self.value, self.allow_unknowns, self.unknowns_specification, self.warnings)
 
class _ValidatedInputFunction():
    def __init__(self, f,
                    passed,
                    value,
                    allow_unknowns,
                    unknowns_spec,
                    warnings):
        self.f = f
        self.passed = passed
        self.value = value
        self.allow_unknowns = allow_unknowns
        self.unknowns_spec = unknowns_spec
        self.validate = True
        self.f_parameters = signature(f).parameters.items()
        self.has_Specification = [name for (name, param) in self.f_parameters
                      if ((param.annotation is not inspect._empty) and (isinstance(param.annotation, Specification)))]
        self.spec_dict=builtins.dict()
        self.defaults = builtins.dict()
        for name,param in self.f_parameters:
            if name in self.has_Specification:
                if param.kind == 4:#kwargs
                    self.spec_dict[name] = Dict(key_spec=String, value_spec=param.annotation)
                elif param.kind == 2:#args
                    self.spec_dict[name] = Iterable(value_spec=param.annotation)
                else:
                    self.spec_dict[name] = param.annotation        
            else:
                self.spec_dict[name] = None
            if param.default is not inspect._empty: 
                self.defaults[name] = param.default#Maybe deepcopy the defaults. In that case, this needs to be moved into each function call
        self.warned = not warnings
        functools.update_wrapper(self, self.f)
    
    def __get__(self,obj,type=None):  # @ReservedAssignment
        return functools.partial(self,obj)
    
    def __call__(self, *args, **kwargs):
        if self.validate:
            if not self.warned:
                validation_start = timeit.default_timer()
            check_dict = builtins.dict()
            args = list(args)
            try_args, try_kwargs = True, True
            for name, param in self.f_parameters:
                if param.kind not in [2, 4]:#Neither *args nor **kwargs
                    v = NotPassed
                    if param.kind == 3 and args:  # When does this happen?
                        raise ValueError("Parameter `{}` is keyword-only".format(name))
                    if try_args and args:
                        v = args.pop(0)
                    elif name in kwargs:
                        v = kwargs.pop(name)
                    if Passed(v):#NotPassed entries won't be validated. If they have a specification, they will be filled with NotPassed later on before 
                        #calling f, otherwise they will not be passed to $f$
                        check_dict[name] = v
                elif param.kind == 2:
                    if args:
                        v = args
                        try_args = False
                        check_dict[name] = v
                elif param.kind == 4:
                    if kwargs:
                        v = kwargs
                        check_dict[name] = v
                        try_kwargs = False
            if (try_args and args) or (try_kwargs and kwargs):  # More passed than expected
                if (try_args and args):
                    raise TypeError('{} was given {} too many positional arguments: {}'.format(self.f.__qualname__, len(args),args))
                if (try_kwargs and kwargs):
                    raise TypeError('{} was given {} unrecognized keyword arguments: {}'.format(self.f.__qualname__, len(kwargs),kwargs))
            try:
                check_dict = _validate_many(args=check_dict, specs=self.spec_dict, defaults=self.defaults,
                    passed_conditions=self.passed,
                    value_conditions=self.value,
                    allow_unknowns=self.allow_unknowns,
                    unknowns_spec=self.unknowns_spec
                ) 
            except ValidationError as e:
                raise TypeError(str(e)) from None
            call_args = []
            call_kwargs = {}
            fill = 'args'
            for name, param in self.f_parameters:
                if not param.kind in [2, 4]:
                    if fill == 'args':
                        call_args.append(check_dict[name])
                    else:
                        call_kwargs[name] = check_dict[name]
                elif param.kind == 2:
                    call_args += check_dict[name]
                    fill = 'kwargs'
                elif param.kind == 4:
                    call_kwargs.update(check_dict[name])
            if not self.warned:
                validation_time = timeit.default_timer() - validation_start
                f_start = timeit.default_timer()
            out = self.f(*call_args, **call_kwargs)
            if not self.warned:
                f_time = timeit.default_timer() - f_start
                factor = validation_time / f_time
                if factor > 2 and self.warned == False:
                    self.warned = True
                    warnings.warn('Costly validation of function {} in {} (Factor {})'.format(self.f.__qualname__, self.f.__module__, factor))
            return out
        else:
            return self.f(*args, **kwargs)

class DefaultGenerator():
    def __init__(self,obj):
        self.obj=obj
    def __call__(self):
        return self.obj()
  
class _Connection(Specification):    
    def __init__(self, *specs, connective):
        self.specs = specs
        self.connective = connective
    def _validate(self, arg):
        rejection_reason = ''
        for spec in self.specs:
            try:
                arg = validate(arg, spec)
            except Exception as e:
                if e.args: 
                    rejection_reason += str(e) 
                #if self.connective == _and:  # Short circuit: invalid. ## Cannot short circuit, otherwise Positive&Integer wouldn't work on string argument, for example
                #    raise ValidationError(rejection_reason)
            else:
                if self.connective == _or:  # Short circuit: valid
                    return arg
        if self.valid(arg):
            return arg
        else:
            raise ValidationError(rejection_reason)
        return arg
    def valid(self, arg):
        return self.connective(spec.valid(arg) for spec in self.specs)
    def __str__(self):
        return '('+self.connective.__str__.join(str(spec) for spec in self.specs)+')'

class Equals(Specification):
    def __init__(self, other):
        self.other = other
    def valid(self, arg):
        return arg == self.other
    def __str__(self):
        return ('Equals({})'.format(self.other))
class Not(Specification):
    def __init__(self,other):
        self.other = other
    def valid(self,arg):
            return arg != self.other
    def __str__(self):
        return ('Not({})'.format(self.other))
class Sum(Specification):
    def __init__(self, s):
        self.s = s
    def valid(self, arg):
        if hasattr(arg, 'values'):
            try:
                lis = arg.values()
            except Exception:
                pass
        else:
            lis = arg
        try:
            s = sum(lis)
            return s == self.s
        except Exception:
            pass
        return False
            
class _Bool(Specification):
    @staticmethod
    def valid(arg):
        return isinstance(arg, builtins.bool)
    @staticmethod
    def forgive(arg, level):
        if level == 1:
            if arg in ['True', 'true']:
                return True
            if arg in ['False', 'false']:
                return False
        if level == 2:
            return builtins.bool(arg)
    def __str__(self):
        return 'Bool'
Bool = _Bool()

class _String(Specification):
    @staticmethod
    def valid(arg):
        return isinstance(arg, six.string_types)
    @staticmethod
    def forgive(arg, level):
        if level == 1:
            if NotPassed(arg):
                return ''
        if level == 2:
            return builtins.str(arg)
    def __str__(self):
        return 'String'
String = _String()

class _Float(Specification):
    @staticmethod
    def valid(arg):
        return isinstance(arg, builtins.float)
    @staticmethod
    def forgive(arg, level):
        if level == 1:
            try:
                return float(arg)
            except Exception:
                pass
    def __str__(self):
        return 'Float'
Float = _Float()

class _Integer(Specification):
    @staticmethod
    def valid(arg):
        return (isinstance(arg, builtins.int) and (arg is not False) and (arg is not True)) or arg == math.inf
    @staticmethod
    def forgive(arg, level):
        if level == 1:
            if isinstance(arg, six.string_types):
                arg = float(arg)
            if isinstance(arg, builtins.float):
                if arg.is_integer():
                    return int(arg)
                elif arg == math.inf:
                    return arg
            if isinstance(arg, numpy.ndarray) and issubclass(arg.dtype, numbers.Integral):
                try:
                    return int(arg)
                except Exception:
                    pass
        if level == 2:
            return int(arg)  
    def __str__(self):
        return 'Integer'
Integer = _Integer()
     
class NDim(Specification):
    def __init__(self, ndim, lenience=1):
        if not isinstance(ndim, builtins.int):
            raise TypeError('`ndim` must be an integer')
        self.ndim = ndim
        super().__init__(lenience)
    def valid(self, arg):
        return arg.ndim == self.ndim
    def forgive(self, arg, level):
        if level == 1:
            t = arg.squeeze()
            while t.ndim < self.ndim:
                t = numpy.expand_dims(t, axis=-1)
            return t
    def __str__(self):
        return 'NDim({})'.format(self.ndim)
    
class _Tuple(Specification):
    def __init__(self, value_spec=NotPassed, lenience=1):
        if not (NotPassed(value_spec) or isinstance(value_spec, Specification)):
            raise TypeError('`value_spec` must be instance of `Specification`')
        self.value_spec = value_spec
        super().__init__(lenience)
    def valid(self, arg):
        return isinstance(arg, builtins.tuple)
    def _validate(self, arg):
        if not self.valid(arg):
            raise ValidationError('Not a tuple')
        if self.value_spec:
            l = [validate(entry, self.value_spec) for entry in arg]
            if any(list_entry != tuple_entry for (list_entry, tuple_entry) in zip(l, arg)):
                return builtins.tuple(l)
            else:
                return arg
        else:
            return arg
    def forgive(self, arg, level):
        if level == 1:
            if NotPassed(arg):
                return ()
            if not isinstance(arg, six.string_types):
                return builtins.tuple(arg)
        if level == 2:
            return (arg,)
    def __str__(self):
        return 'Tuple{}'.format('({})'.format(self.value_spec) if self.value_spec else '')
Tuple = _Tuple()

class Shape(Specification):
    def __init__(self, shape, lenience=1):
        if not isinstance(shape, (builtins.list, builtins.tuple)):
            raise TypeError('`shape` must be list of integers')
        self.shape = shape
        super().__init__(lenience)
    def valid(self, arg):
        return arg.shape == self.shape
    def forgive(self, arg, level):
        if level == 1:
            if numpy.squeeze(arg).shape == numpy.squeeze(numpy.zeros(self.shape)).shape:
                return arg.reshape(self.shape)
        if level == 2:
            return arg.reshape(self.shape)
    def __str__(self):
        return 'Shape({})'.format(self.shape)


class _ValidatedOutputFunction():
    def __init__(self, fn, value_spec):
        self.fn = fn
        self.value_spec = value_spec  
    def __call__(self, *args, **kwargs):
        return validate(self.fn(*args, **kwargs), self.value_spec)

class _Function(Specification):
    def __init__(self, value_spec=NotPassed, lenience=1):
        if not (NotPassed(value_spec) or isinstance(value_spec, Specification)):
            raise TypeError('`value_spec` must be instance of `Specification`')
        if Passed(value_spec):
            self.value_spec = validate(value_spec, Instance(Specification))
        self.value_spec = value_spec
        super().__init__(lenience)
    def forgive(self, arg, level):
        if level == 1:
            if Passed(self.value_spec):
                validate(arg, self.value_spec)
            return lambda x:arg  # Value will also be checked when needed
    def valid(self, arg):
        return hasattr(arg, '__call__')
    def _validate(self, arg):
        if self.valid(arg):
            if Passed(self.value_spec):
                return _ValidatedOutputFunction(arg, self.value_spec)
            else:
                return arg
        else:
            raise ValidationError
    def __str__(self):
        return 'Function{}'.format('({})'.format(self.value_spec) if self.value_spec else '')
Function = _Function()

class _Dict(Specification):
    def __init__(self, key_spec=NotPassed, value_spec=NotPassed, lenience=1, passed_conditions=NotPassed):
        if not (NotPassed(key_spec) or isinstance(key_spec, Specification)):
            raise TypeError('`key_spec` must be instance of `Specification`')
        if not (NotPassed(value_spec) or isinstance(value_spec, Specification)):
            raise TypeError('`value_spec` must be instance of `Specification`')
        if not (NotPassed(passed_conditions) or isinstance(passed_conditions, six.string_types)):
            raise TypeError('`passed_conditions` must be a string')
        self.key_spec = key_spec
        self.value_spec = value_spec
        self.passed_conditions = passed_conditions
        self.required_results_iterables_and_connectives = []
        if Passed(passed_conditions):  # Only _parse_condition would be needed if we didn't want to allow writing (a,b,c)>d as shorthand for a>d b>d c>d
            for condition in [r for r in self.passed_conditions.split(' ') if r != '']:
                required_results_groups, connective = _parse_condition(condition)
                required_results_groups = [_parse_required_results_group(required_results_group) for required_results_group in required_results_groups]
                required_results_iterable = list(itertools.product(*(required_results_group.items() for required_results_group in required_results_groups)))
                self.required_results_iterables_and_connectives.append((required_results_iterable, connective))
        super().__init__(lenience)
    def valid(self, arg):
        return isinstance(arg, builtins.dict)
    def _validate(self, arg):
        if not self.valid(arg):
            raise ValidationError('Not a dictionary')
        if Passed(self.value_spec) or Passed(self.key_spec):
            if NotPassed(self.value_spec):
                self.value_spec = Any
            if NotPassed(self.key_spec):
                self.key_spec = Any
            l = [(validate(key, self.key_spec), validate(arg[key], self.value_spec)) for key in arg]
            if any(list_item != dict_item for (list_item, dict_item) in zip(l, arg.items())):
                arg = builtins.dict(l)
        if self.required_results_iterables_and_connectives:
            arg = _validate_dict_conditions(arg, self.required_results_iterables_and_connectives, type='passed')
        return arg 
    def forgive(self, arg, level):
        if level == 1 and not self.valid(arg):
            if NotPassed(arg):
                return builtins.dict()
            try:
                return builtins.dict(arg)
            except Exception:
                pass
        if level == 2:
            if isinstance(arg, (builtins.list, builtins.tuple)) or (isinstance(arg,numpy.ndarray) and arg.squeeze().ndim == 1):
                d = builtins.dict()
                for i in range(len(arg)):
                    d[i] = arg[i]
                return d
    def __str__(self):
        init_arguments = (self.key_spec, self.value_spec, self.passed_conditions)
        out = 'Dict'
        if any(Passed(init_argument) for init_argument in init_arguments):
            out += '('
            if any(Passed(init_argument) for init_argument in init_arguments[:2]):
                out += 'key_spec={},value_spec={},'.format(*init_arguments[:2])
            if any(Passed(init_argument) for init_argument in init_arguments[2:]):
                out += 'passed_conditions=\'{}\','.format(*init_arguments[2:])
            out = out[:-1] + ')'
        return out
Dict = _Dict()

class In(Specification):
    def __init__(self, *choices, lenience=1):
        self.choices = choices
        self.mod_choices = tuple(self.choices)
        super().__init__(lenience)
    def valid(self, arg):
        return arg in self.choices
    def forgive(self, arg, level):
        if level == 1:  # Forgive capitalization
            if isinstance(arg, six.string_types):
                string_choices = [choice for choice in self.choices if isinstance(choice, six.string_types)]
                # Reasoning: If different first letter capitalization sure capitalization has l meaning, so no forgiving
                # If same first letter capitalization, but pairs like AB vs. Ab occur then of course also no forgiving 
                if all(s[0].isupper() for s in string_choices) or all(s[0].islower() for s in string_choices):
                    mod_choices = [choice.lower() if hasattr(choice, 'lower') else choice for choice in self.choices]  # keep non string choices so that index below works
                    if len(set(mod_choices)) == len(mod_choices) and arg.lower() in mod_choices:
                        self.mod_choices = mod_choices
                        return self.choices[self.mod_choices.index(arg.lower())]
        if level == 2:  # Forgive abbreviations
            l = 0
            if isinstance(arg, six.string_types):
                string_choices = [choice for choice in self.choices if isinstance(choice, six.string_types)]
                if all(s[0].isupper() for s in string_choices) or all(s[0].islower() for s in string_choices):
                    arg = arg.lower()
                    mod_choices = [choice.lower() if hasattr(choice, 'lower') else choice for choice in self.choices]
                else:
                    mod_choices = self.choices
                if len(set(mod_choices)) == len(mod_choices):
                    for l in range(max(len(s) for s in string_choices)):
                        l += 1
                        inits = [choice[:l] if isinstance(choice, six.string_types) else choice for choice in mod_choices ] 
                        if len(inits) == len(set(inits)) and arg in inits:
                            return self.choices[inits.index(arg)]
    def __str__(self):
        return 'In(' + ','.join(str(spec) for spec in self.choices) + ')'
    
class _Set(Specification):
    def __init__(self, value_spec=NotPassed, lenience=1):
        if not (NotPassed(value_spec) or isinstance(value_spec, Specification)):
            raise TypeError('`value_spec` must be instance of `Specification`')
        self.value_spec = value_spec
        super().__init__(lenience)
    def valid(self, arg):
        return isinstance(arg, builtins.set)
    def _validate(self, arg):
        if not self.valid(arg):
            raise ValidationError('Not a set')
        if self.value_spec:
            l = [validate(entry, self.value_spec) for entry in arg]
            if any(list_entry != set_entry for (list_entry, set_entry) in zip(l, arg)):
                return builtins.set(l)
            else:
                return arg
        else:
            return arg
    def forgive(self, arg, level):
        if level == 1:  # Convert iterables with unique entries
            if NotPassed(arg):
                return {}
            if not isinstance(arg, six.string_types):
                temp = builtins.set(arg)
                if len(temp) == len(arg):
                    return temp
        if level == 2:  # Convert lists with repetitions and single objects
            if not isinstance(arg, six.string_types):
                try:
                    return set(arg)
                except Exception:
                    pass
            return {arg}
    def __str__(self):
        return 'Set{}'.format('({})'.format(self.value_spec) if self.value_spec else '')
Set = _Set()

class _List(Specification):
    def __init__(self, value_spec=NotPassed, lenience=1):
        if not (NotPassed(value_spec) or isinstance(value_spec, Specification)):
            raise TypeError('`value_spec` must be instance of `Specification`')
        self.value_spec = value_spec
        super().__init__(lenience)
    def _validate(self, arg):
        if not self.valid(arg):
            raise ValidationError('Not a list')
        if self.value_spec:
            l = [validate(entry, self.value_spec) for entry in arg]
            if any(list_entry != tuple_entry for (list_entry, tuple_entry) in zip(l, arg)):
                return l
            else:
                return arg
        else:
            return arg
    def forgive(self, arg, level):
        if level == 1:
            if NotPassed(arg):
                return []
            if not isinstance(arg, six.string_types):
                return builtins.list(arg)
        if level == 2:
            return [arg]
    def valid(self, arg):  # CHECK!
        return isinstance(arg, builtins.list)
    def __str__(self):
        return 'List{}'.format('({})'.format(self.value_spec) if self.value_spec else '')
List = _List()

class _Lower(Specification):
    @staticmethod
    def valid(arg):
        return hasattr(arg, 'lower') and arg.lower() == arg
    @staticmethod
    def forgive(arg, level):
        if level == 2:
            if hasattr(arg, 'lower'):
                return arg.lower()
    def __str__(self):
        return 'Lower'
Lower = _Lower()

class _Upper(Specification):
    @staticmethod
    def valid(arg):
        return hasattr(arg, 'upper') and arg.upper() == arg
    @staticmethod
    def forgive(arg, level):
        if level == 2:
            if hasattr(arg, 'upper'):
                return arg.upper()
    def __str__(self):
        return 'Upper'
Upper = _Upper()

class InInterval(Specification):
    def __init__(self, l=-math.inf, r=math.inf, lo=False, ro=False, lenience=1):
        self.l = l
        self.r = r
        self.lo = lo
        self.ro = ro
        self.lenience = lenience
    def valid(self, arg):
        if not (isinstance(arg, numbers.Number) and type(arg) != builtins.bool):
            return False
        if self.lo:
            if arg <= self.l:
                return False
        else:
            if arg < self.l:
                return False
        if self.ro:
            if arg >= self.r:
                return False 
        else:
            if arg > self.r:
                return False
        return True
    def forgive(self, arg, level):
        if level == 1:
            try:
                return ast.literal_eval(arg)
            except Exception:
                pass 
        if level == 2:
            try:
                if not self.lo:
                    arg = max(arg, self.l)
                if not self.ro:
                    arg = min(arg, self.r)
                return arg
            except Exception:
                pass
    def __str__(self):
        return 'InInterval(l={},r={},lo={},ro={})'.format(self.l, self.r, self.lo, self.ro)

class InRange(InInterval):
    def __init__(self, l, r=NotPassed, lenience=1):
        if NotPassed(r):
            r = l
            l = 0
        super().__init__(lenience=lenience, l=l, r=r, lo=False, ro=True)    

class _Any(Specification):
    def __init__(self, description=NotPassed):
        self.description = description
    def valid(self, arg):
        return True
Any = _Any()

class Length(Specification):
    def __init__(self, l_min, l_max=NotPassed, lenience=1):
        self.l_min = l_min
        if Passed(l_max):
            self.l_max = l_max
        else:
            self.l_max = l_min
        self.lenience = lenience
    def valid(self, arg):
        return self.l_min <= len(arg) <= self.l_max
    def __str__(self):
        return 'Length(l_min={},l_max={})'.format(self.l_min, self.l_max)
    
class _Iterable(Specification):
    def __init__(self, value_spec=NotPassed, lenience=1):
        super().__init__(lenience)
        self.value_spec = value_spec
    def valid(self, arg):
        try:
            validate(arg, Allows('__iter__'))
            if not isinstance(arg, six.string_types):
                return True
        except ValidationError:
            pass
        return False
    def _validate(self, arg):
        if NotPassed(arg):
            arg = ()
        if not self.valid(arg) and self.lenience == 2:
            arg = (arg,)
        if self.valid(arg):
            if Passed(self.value_spec):
                return ValidatedIterable(arg, self.value_spec)
            else:
                return arg
        else:
            raise ValidationError
    def __str__(self):
        return 'Iterable{}'.format('({})'.format(self.value_spec) if self.value_spec else '')
Iterable = _Iterable()     
class ValidatedIterable():
    def __init__(self, iterable, value_specification):
        self.iterable = iterable
        self.value_specification = value_specification
    def __iter__(self):
        checks = zip(self.iterable, itertools.repeat(self.value_specification))
        for v, value_specification in checks:
            yield validate(v, spec=value_specification)

class Allows(Specification):  # Checks if objects have methods (including classmethods and staticmethods)
    def __init__(self, *fn_names, lenience=1):
        self.lenience = lenience
        self.fn_names = fn_names
    def valid(self, arg):
        try:
            return all(Function.valid(getattr(arg, fn_name)) for fn_name in self.fn_names)
        except Exception:
            pass
    def __str__(self):
        return 'Allows(' + ','.join(fn_name for fn_name in self.fn_names) + ')'

class Has(Specification):
    def __init__(self, *attr_names, lenience=1):
        self.lenience = lenience
        self.attr_names = attr_names
    def valid(self, arg):
        return all(hasattr(arg, attr_name) for attr_name in self.attr_names)
    def __str__(self):
        return 'Has(' + ','.join(attr_name for attr_name in self.attr_names) + ')'

class Implements(Specification):
    def __init__(self, *declarations, lenience=1):
        if any(not isinstance(declaration, default) for declaration in declarations):
            fail = [declaration for declaration in declarations if not isinstance(declaration, default)]
            raise ValueError('{} {} not of type `declaration`'.format(fail, 'is' if len(fail) == 1 else 'are'))
        self.lenience = lenience
        self.declarations = declarations
    def valid(self, arg):
        try:
            return all(find_implementation(arg.__class__, declaration) for declaration in self.declarations)
        except Exception:
            pass
    def __str__(self):
        return 'Implements(' + ','.join(str(declaration) for declaration in self.declarations) + ')'
    
class Instance(Specification):
    def __init__(self, cl, lenience=1):
        if not inspect.isclass(cl):
            raise TypeError('`cl` must be a class')
        self.cl = cl
        super().__init__(lenience)
    def valid(self, arg):
        return isinstance(arg, self.cl)
    def forgive(self, arg, level):
        if level == 1:
            if self.cl not in (builtins.int, builtins.str, builtins.bool):  # Constructors of these classes are too forgiving 
                return self.cl(arg)
        if level == 2:
            return self.cl(arg)
    def __str__(self):
        return 'Instance({})'.format(self.cl.__qualname__)
    
class Satisfies(Specification):
    def __init__(self, *checks, lenience=1):
        self.checks = checks
        self.lenience = lenience
    def valid(self, arg):
        return all(check(arg) for check in self.checks)
    def __str__(self):
        return 'Satisfies(' + ','.join(str(check) for check in self.checks) + ')'
    
class _Nonnegative(InInterval):
    def __init__(self, lenience=1):
        super().__init__(lenience=lenience, l=0, r=inf, lo=False, ro=False) 
Nonnegative = _Nonnegative()

class _Positive(InInterval):
    def __init__(self, lenience=1):
        super().__init__(lenience=lenience, l=0, r=inf, lo=True, ro=False) 
Positive = _Positive()

class _Nonpositive(InInterval):
    def __init__(self, lenience=1):
        super().__init__(lenience=lenience, l=-inf, r=0, lo=False, ro=False) 
Nonpositive = _Nonpositive()

class _Negative(InInterval):
    def __init__(self, lenience=1):
        super().__init__(lenience=lenience, l=-inf, r=0, lo=False, ro=True) 
Negative = _Negative()

def _parse_condition(req, seps=['|', '^', '>', '==']):
    # seps = ['|', '^', '>', '-']
    possible_types = [sep for sep in seps if sep in req]
    if len(possible_types) > 1:
        raise ValueError('Each condition can only contain one of the following connectives: {}. '.format(seps) + 
                            'Multiple requirements must be separated by a space character')
    # if len(possible_types)==0:
    #    raise ValueError('Only the following connectives are allowed:{}'.format(possible_types))
    if '|' in req:
        args, req_type = req.split('|'), 'or'
    elif '^' in req:
        args, req_type = req.split('^'), 'xor'
    elif '==' in req:
        args, req_type = req.split('=='), 'iff'
    elif '>' in req:
        if req.count('>') > 1:
            raise ValueError('The implication, `>`, can only occur once in each condition. Multiple conditions must be separated by a space character')
        args, req_type = req.split('>', 1), 'implies'
    elif '&' in req:
        args, req_type = req.split('&'), 'and'
    else:
        args, req_type = (req,), 'require'
    return args, req_type

def _parse_required_results_group(subject_group):
    if not isinstance(subject_group, six.string_types):
        raise TypeError('subject_group must be a string')
    if subject_group.count('(') > 1 or subject_group.count(')') > 1:
        raise ValueError('Groups of parameters cannot be nested')
    subject = subject_group.strip('( )')
    single_results = subject.split(',')
    parameters_and_results = {single_result.replace('~', ''):bool((1 + single_result.count('~')) % 2) for single_result in single_results}
    if not all(parameter.isidentifier() for parameter in parameters_and_results):
        raise ValueError('Malformed dictionary condition: {}.'.format(subject_group) + 
                         (' Use only the connectives `^`,`|` and `->`' if '&' in subject_group else ''))
    return parameters_and_results

def _validate_dict_conditions(args:Dict, required_results_iterables_and_connectives, type='passed'):  # @ReservedAssignment
    if not isinstance(args, builtins.dict):
        raise TypeError('`args` must be a dict')
    if not isinstance(required_results_iterables_and_connectives, (builtins.list, builtins.tuple)):
        raise TypeError('`required_results_iterables_and_connectives` must be a list')
    if not type in ('passed', 'bool'):
        raise TypeError('`type` must be either "parsed" or "boolean"')
    args_copy = defaultdict(lambda: NotPassed)
    args_copy.update(args)
    if type == 'passed':
        evaluation = lambda x: x in args_copy and Passed(args_copy[x])
    elif type == 'bool':
        evaluation = lambda x: x in args_copy and bool(args_copy[x])
    condition_string = lambda required_result: type + '(' + required_result[0] + ')' + ('=' if required_result[1] else '~') + '=True'
    for (required_results_iterable, connective) in required_results_iterables_and_connectives:
        if connective == 'or':
            for required_results in required_results_iterable:
                if all(required_result[1] != evaluation(required_result[0]) for required_result in required_results):
                    raise ValidationError('At least one of [{}] must hold'.format(','.join(condition_string(required_result) for required_result in required_results)))
        elif connective == 'implies':
            for (left, right) in required_results_iterable:
                if left[1] == evaluation(left[0]) and right[1] != evaluation(right[0]):
                    raise ValidationError('If  {}, then {} hold as well as well'.format(condition_string(left), condition_string(right)))
        elif connective == 'xor':
            for required_results in required_results_iterable:
                matches = [required_result[1] == evaluation(required_result[0]) for required_result in required_results]
                if matches.count(True) != 1:
                    raise ValidationError('Exactly one of [{}] must hold'.format(','.join(condition_string(required_result) for required_result in required_results)))
        elif connective == 'require':
            for required_results in required_results_iterable:
                required_result = required_results[0]  # Only one subject
                if required_result[1] != evaluation(required_result[0]):
                    raise ValidationError('{} must hold'.format(condition_string(required_result)))
        elif connective == 'iff':
            for required_results in required_results_iterable:
                matches = [required_result[1] == evaluation(required_result[0]) for required_result in required_results]
                if matches.count(True) not in (0, len(required_results)):
                    raise ValidationError('All or none of [{}] must hold'.format(','.join(condition_string(required_result) for required_result in required_results))) 
    return args

class Arg(Specification):
    '''
    Validates entries of a dictionary. 
    
    E.g.: `Arg('a>b')` ensures that `b` evaluates to True if `a` does
          `Arg('a&b',Lower)` ensures that `a` and `b` are both `Lower`
          `Arg('a^b',Positive)` ensures that exactly one of `a` and `b` are positive
    '''
    def __init__(self, names, spec=NotPassed):
        self.names, connective = _parse_condition(names, seps=['&', '|', '^', '>', '=='])
        if connective == 'and':
            self.connective = _and
        elif connective == 'or':
            self.connective = _or
        elif connective == 'require':  # only one name
            self.connective = _and
        elif connective == 'implies':
            self.connective = _implies
        elif connective == 'xor':
            self.connective = _xor
        elif connective == 'iff':
            self.connective = _equal
        if not (NotPassed(spec) or isinstance(spec, Specification) or spec == Passed or spec == NotPassed):
            raise TypeError('`spec` must be instance of `Specification`')
        self.spec = spec 
    def valid(self, args):
        if Passed(self.spec):
            return self.connective(self.spec.valid(args[name]) for name in self.names)
        else:
            return self.connective(bool(args[name]) for name in self.names)
    def __str__(self):
        return 'Arg({}{})'.format(self.connective.__str__.join(self.names), ',{}'.format(self.spec) if Passed(self.spec) else '')
    def __or__(self, other):
        return _Connection(self, other, connective=_or)
    def __and__(self, other):
        return _Connection(self, other, connective=_and)  

def _and(bools):
    return all(bools)
def _implies(bools):
    bools = list(bools)
    return bools[1] or not bools[0]
def _or(bools):
    return any(bools)
def _xor(bools):
    return len([b for b in bools if b]) == 1
def _equal(bools):
    bools = list(bools)
    return len([b for b in bools if b]) in (0, len(bools))
_and.__str__ = ' & '
_implies.__str__ = ' > '
_or.__str__ = ' | '
_xor.__str__ = ' ^ '
_equal.__str__ = ' == '
