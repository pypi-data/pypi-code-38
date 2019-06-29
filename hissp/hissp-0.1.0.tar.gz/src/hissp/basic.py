__import__('operator').setitem(
  globals(),
  '_macro_',
  __import__('types').ModuleType(
    '_macro_'))

setattr(
  _macro_,
  'requirexH_as',
  (lambda macro,name:
    (lambda *xAUTO0_:xAUTO0_)(
      'builtins..setattr',
      (lambda *xAUTO0_:xAUTO0_)(
        '.setdefault',
        (lambda *xAUTO0_:xAUTO0_)(
          'builtins..globals'),
        (lambda *xAUTO0_:xAUTO0_)(
          'quote',
          '_macro_'),
        (lambda *xAUTO0_:xAUTO0_)(
          'types..ModuleType',
          (lambda *xAUTO0_:xAUTO0_)(
            'quote',
            'hissp.basic.._macro_'))),
      (lambda *xAUTO0_:xAUTO0_)(
        'quote',
        name),
      macro)))

setattr(
  _macro_.requirexH_as,
  '__doc__',
  "\nRequire a macro callable as an unqualified name.\n\nAdds the macro to the current module's _macro_ space under the specified\nname, which makes it available unqualified in this module. (And\navailable qualified with this module's name.)\n")

setattr(
  _macro_.requirexH_as,
  '__qualname__',
  '_macro_.requirexH_as')

# requirexH_as
__import__('builtins').setattr(
  __import__('builtins').globals().setdefault(
    '_macro_',
    __import__('types').ModuleType(
      'hissp.basic.._macro_')),
  'defmacro',
  (lambda name,parameters,*body:
    (lambda *xAUTO0_:xAUTO0_)(
      'hissp.basic.._macro_.requirexH_as',
      (lambda *xAUTO0_:xAUTO0_)(
        'lambda',
        parameters,
        *body),
      name)))

# defmacro
# hissp.basic.._macro_.requirexH_as
__import__('builtins').setattr(
  __import__('builtins').globals().setdefault(
    '_macro_',
    __import__('types').ModuleType(
      'hissp.basic.._macro_')),
  'let',
  (lambda pairs,*body:
    (lambda *xAUTO0_:xAUTO0_)(
      (lambda *xAUTO0_:xAUTO0_)(
        'lambda',
        (lambda *xAUTO0_:xAUTO0_)(
          ':',
          *pairs),
        *body))))

setattr(
  _macro_.let,
  '__doc__',
  '\nCreates locals. Pairs are implied. Locals are not in scope until the body.\n')

setattr(
  _macro_.let,
  '__qualname__',
  '_macro_.let')

# defmacro
# hissp.basic.._macro_.requirexH_as
__import__('builtins').setattr(
  __import__('builtins').globals().setdefault(
    '_macro_',
    __import__('types').ModuleType(
      'hissp.basic.._macro_')),
  'defmacro',
  (lambda name,parameters,docstring,*body:
    (lambda *xAUTO0_:xAUTO0_)(
      'hissp.basic.._macro_.requirexH_as',
      (lambda *xAUTO0_:xAUTO0_)(
        'hissp.basic.._macro_.let',
        (lambda *xAUTO0_:xAUTO0_)(
          '_macroxAUTO4_',
          (lambda *xAUTO0_:xAUTO0_)(
            'lambda',
            parameters,
            *body)),
        (lambda *xAUTO0_:xAUTO0_)(
          'builtins..setattr',
          '_macroxAUTO4_',
          (lambda *xAUTO0_:xAUTO0_)(
            'quote',
            '__doc__'),
          docstring),
        (lambda *xAUTO0_:xAUTO0_)(
          'builtins..setattr',
          '_macroxAUTO4_',
          (lambda *xAUTO0_:xAUTO0_)(
            'quote',
            '__qualname__'),
          (lambda *xAUTO0_:xAUTO0_)(
            '.join',
            ('quote', '.', {':str': True}),
            (lambda *xAUTO0_:xAUTO0_)(
              'quote',
              (lambda *xAUTO0_:xAUTO0_)(
                '_macro_',
                name)))),
        '_macroxAUTO4_'),
      name)))

setattr(
  _macro_.defmacro,
  '__doc__',
  '\nCreates a new macro for the current module.\n\nThe docstring argument is required, but can be None.\n')

setattr(
  _macro_.defmacro,
  '__qualname__',
  '_macro_.defmacro')

# defmacro
# hissp.basic.._macro_.requirexH_as
__import__('builtins').setattr(
  __import__('builtins').globals().setdefault(
    '_macro_',
    __import__('types').ModuleType(
      'hissp.basic.._macro_')),
  'cascade',
  # hissp.basic.._macro_.let
  (lambda _macroxAUTO4_=(lambda thing,*calls:
    # let
    (lambda thingxH_sym='_thingxAUTO5_':
      (lambda *xAUTO0_:xAUTO0_)(
        (lambda *xAUTO0_:xAUTO0_)(
          'lambda',
          (lambda *xAUTO0_:xAUTO0_)(
            ':',
            thingxH_sym,
            thing),
          *map(
            (lambda call:
              (lambda *xAUTO0_:xAUTO0_)(
                __import__('operator').getitem(
                  call,
                  (0)),
                thingxH_sym,
                *__import__('operator').getitem(
                  call,
                  slice(
                    (1),
                    None)))),
            calls),
          thingxH_sym)))()):(
    __import__('builtins').setattr(
      _macroxAUTO4_,
      '__doc__',
      'Call multiple methods on one object.\n\n  Evaluates the given thing then uses it as the first argument to a\n  sequence of calls. Used for initialization. Evaluates to the thing.\n  '),
    __import__('builtins').setattr(
      _macroxAUTO4_,
      '__qualname__',
      '.'.join(
        ('_macro_', 'cascade'))),
    _macroxAUTO4_)[-1])())

# defmacro
# hissp.basic.._macro_.requirexH_as
__import__('builtins').setattr(
  __import__('builtins').globals().setdefault(
    '_macro_',
    __import__('types').ModuleType(
      'hissp.basic.._macro_')),
  'define',
  # hissp.basic.._macro_.let
  (lambda _macroxAUTO4_=(lambda name,value:
    (lambda *xAUTO0_:xAUTO0_)(
      'operator..setitem',
      (lambda *xAUTO0_:xAUTO0_)(
        'builtins..globals'),
      (lambda *xAUTO0_:xAUTO0_)(
        'quote',
        name),
      value)):(
    __import__('builtins').setattr(
      _macroxAUTO4_,
      '__doc__',
      'Assigns a global in the current module.'),
    __import__('builtins').setattr(
      _macroxAUTO4_,
      '__qualname__',
      '.'.join(
        ('_macro_', 'define'))),
    _macroxAUTO4_)[-1])())

# defmacro
# hissp.basic.._macro_.requirexH_as
__import__('builtins').setattr(
  __import__('builtins').globals().setdefault(
    '_macro_',
    __import__('types').ModuleType(
      'hissp.basic.._macro_')),
  'ifxH_else',
  # hissp.basic.._macro_.let
  (lambda _macroxAUTO4_=(lambda test,then,otherwise:
    (lambda *xAUTO0_:xAUTO0_)(
      (lambda *xAUTO0_:xAUTO0_)(
        'lambda',
        (lambda *xAUTO0_:xAUTO0_)(
          'test',
          ':',
          ':*',
          'thenxH_else'),
        (lambda *xAUTO0_:xAUTO0_)(
          (lambda *xAUTO0_:xAUTO0_)(
            'operator..getitem',
            'thenxH_else',
            (lambda *xAUTO0_:xAUTO0_)(
              'operator..not_',
              'test')))),
      test,
      (lambda *xAUTO0_:xAUTO0_)(
        'lambda',
        (),
        then),
      (lambda *xAUTO0_:xAUTO0_)(
        'lambda',
        (),
        otherwise))):(
    __import__('builtins').setattr(
      _macroxAUTO4_,
      '__doc__',
      "Basic ternary branching construct.\n\n  Like Python's conditional expressions, the else-clause is required.\n  "),
    __import__('builtins').setattr(
      _macroxAUTO4_,
      '__qualname__',
      '.'.join(
        ('_macro_', 'ifxH_else'))),
    _macroxAUTO4_)[-1])())

# defmacro
# hissp.basic.._macro_.requirexH_as
__import__('builtins').setattr(
  __import__('builtins').globals().setdefault(
    '_macro_',
    __import__('types').ModuleType(
      'hissp.basic.._macro_')),
  'progn',
  # hissp.basic.._macro_.let
  (lambda _macroxAUTO4_=(lambda *body:
    (lambda *xAUTO0_:xAUTO0_)(
      (lambda *xAUTO0_:xAUTO0_)(
        'lambda',
        (),
        *body))):(
    __import__('builtins').setattr(
      _macroxAUTO4_,
      '__doc__',
      'Evaluates each form in sequence for side effects.\n\n  Evaluates to the same value as its last form (or ``()`` if empty).\n  '),
    __import__('builtins').setattr(
      _macroxAUTO4_,
      '__qualname__',
      '.'.join(
        ('_macro_', 'progn'))),
    _macroxAUTO4_)[-1])())

# defmacro
# hissp.basic.._macro_.requirexH_as
__import__('builtins').setattr(
  __import__('builtins').globals().setdefault(
    '_macro_',
    __import__('types').ModuleType(
      'hissp.basic.._macro_')),
  'fromxH_require',
  # hissp.basic.._macro_.let
  (lambda _macroxAUTO4_=(lambda *packagexPLUS_macros:
    (lambda *xAUTO0_:xAUTO0_)(
      'hissp.basic.._macro_.progn',
      (lambda *xAUTO0_:xAUTO0_)(
        '.setdefault',
        (lambda *xAUTO0_:xAUTO0_)(
          'builtins..globals'),
        (lambda *xAUTO0_:xAUTO0_)(
          'quote',
          '_macro_'),
        (lambda *xAUTO0_:xAUTO0_)(
          'types..ModuleType',
          (lambda *xAUTO0_:xAUTO0_)(
            'quote',
            'hissp.basic.._macro_'))),
      *__import__('itertools').starmap(
        (lambda package,*macros:
          (lambda *xAUTO0_:xAUTO0_)(
            'hissp.basic.._macro_.progn',
            *map(
              (lambda macro:
                (lambda *xAUTO0_:xAUTO0_)(
                  'builtins..setattr',
                  '_macro_',
                  (lambda *xAUTO0_:xAUTO0_)(
                    'quote',
                    macro),
                  '{}.._macro_.{}'.format(
                    package,
                    macro))),
              macros))),
        packagexPLUS_macros))):(
    __import__('builtins').setattr(
      _macroxAUTO4_,
      '__doc__',
      'Adds macros for the current module from ``package``\n\n   For example::\n\n    (from-require (foo.package spammacro eggsmacro)\n                  (bar.package baconmacro bannanamacro))\n\n  '),
    __import__('builtins').setattr(
      _macroxAUTO4_,
      '__qualname__',
      '.'.join(
        ('_macro_', 'fromxH_require'))),
    _macroxAUTO4_)[-1])())

# defmacro
# hissp.basic.._macro_.requirexH_as
__import__('builtins').setattr(
  __import__('builtins').globals().setdefault(
    '_macro_',
    __import__('types').ModuleType(
      'hissp.basic.._macro_')),
  'deftype',
  # hissp.basic.._macro_.let
  (lambda _macroxAUTO4_=(lambda name,bases,*body:
    (lambda *xAUTO0_:xAUTO0_)(
      'hissp.basic.._macro_.define',
      name,
      (lambda *xAUTO0_:xAUTO0_)(
        'builtins..type',
        (lambda *xAUTO0_:xAUTO0_)(
          'quote',
          name),
        (lambda *xAUTO0_:xAUTO0_)(
          (lambda *xAUTO0_:xAUTO0_)(
            'lambda',
            (lambda *xAUTO0_:xAUTO0_)(
              ':',
              ':*',
              'xAUTO0_'),
            'xAUTO0_'),
          *bases),
        (lambda *xAUTO0_:xAUTO0_)(
          'builtins..dict',
          ':',
          *body)))):(
    __import__('builtins').setattr(
      _macroxAUTO4_,
      '__doc__',
      'Defines a type (class) in the current module.\n\n  Key-value pairs are implied in the body.\n  '),
    __import__('builtins').setattr(
      _macroxAUTO4_,
      '__qualname__',
      '.'.join(
        ('_macro_', 'deftype'))),
    _macroxAUTO4_)[-1])())

# define
__import__('operator').setitem(
  __import__('builtins').globals(),
  '__doc__',
  "\nHissp's basic macros.\n\nThese are automatically made available as unqualified macros in the\nbasic REPL. To use them in a Hissp module, either use the\nfully-qualified names, or add them to the module's _macro_'s.\n\nFor example::\n\n  (hissp.basic.._macro_.from-require\n   (hissp.basic cascade if-else let progn))\n\n")