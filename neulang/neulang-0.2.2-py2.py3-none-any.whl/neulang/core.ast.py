#==================================================
#AST tree for core.py
#==================================================

Module(body=[
    Expr(value=Str(s='\n\n', lineno=4, col_offset=-1), lineno=4, col_offset=-1),
    Import(names=[
        alias(name='pdb', asname=None),
      ], lineno=7, col_offset=0),
    Import(names=[
        alias(name='traceback', asname='tb'),
      ], lineno=8, col_offset=0),
    ImportFrom(module='ast', names=[
        alias(name='*', asname=None),
      ], level=0, lineno=10, col_offset=0),
    ImportFrom(module='os.path', names=[
        alias(name='exists', asname=None),
      ], level=0, lineno=11, col_offset=0),
    ImportFrom(module='omp', names=[
        alias(name='OMP', asname=None),
      ], level=0, lineno=13, col_offset=0),
    ClassDef(name='Neulang', bases=[], keywords=[], body=[
        FunctionDef(name='__init__', args=arguments(args=[
            arg(arg='self', annotation=None, lineno=18, col_offset=17),
            arg(arg='astir', annotation=None, lineno=18, col_offset=23),
          ], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[
            NameConstant(value=None, lineno=18, col_offset=29),
          ]), body=[
            Assign(targets=[
                Attribute(value=Name(id='self', ctx=Load(), lineno=19, col_offset=8), attr='_astir_file', ctx=Store(), lineno=19, col_offset=8),
              ], value=BoolOp(op=Or(), values=[
                Name(id='astir', ctx=Load(), lineno=19, col_offset=27),
                Str(s='astir.neu', lineno=19, col_offset=36),
              ], lineno=19, col_offset=27), lineno=19, col_offset=8),
            Assign(targets=[
                Attribute(value=Name(id='self', ctx=Load(), lineno=20, col_offset=8), attr='_astir', ctx=Store(), lineno=20, col_offset=8),
              ], value=Call(func=Attribute(value=Name(id='self', ctx=Load(), lineno=20, col_offset=22), attr='load_astir', ctx=Load(), lineno=20, col_offset=22), args=[], keywords=[], lineno=20, col_offset=22), lineno=20, col_offset=8),
            Return(value=None, lineno=21, col_offset=8),
          ], decorator_list=[], returns=None, lineno=18, col_offset=4),
        FunctionDef(name='load_astir', args=arguments(args=[
            arg(arg='self', annotation=None, lineno=23, col_offset=19),
          ], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]), body=[
            If(test=UnaryOp(op=Not(), operand=Call(func=Name(id='exists', ctx=Load(), lineno=24, col_offset=15), args=[
                Attribute(value=Name(id='self', ctx=Load(), lineno=24, col_offset=22), attr='_astir_file', ctx=Load(), lineno=24, col_offset=22),
              ], keywords=[], lineno=24, col_offset=15), lineno=24, col_offset=11), body=[
                Return(value=None, lineno=24, col_offset=41),
              ], orelse=[], lineno=24, col_offset=8),
            Assign(targets=[
                Name(id='am', ctx=Store(), lineno=25, col_offset=8),
              ], value=Call(func=Attribute(value=Name(id='self', ctx=Load(), lineno=25, col_offset=13), attr='load', ctx=Load(), lineno=25, col_offset=13), args=[
                Attribute(value=Name(id='self', ctx=Load(), lineno=25, col_offset=23), attr='_astir_file', ctx=Load(), lineno=25, col_offset=23),
              ], keywords=[], lineno=25, col_offset=13), lineno=25, col_offset=8),
            Return(value=Name(id='am', ctx=Load(), lineno=26, col_offset=15), lineno=26, col_offset=8),
          ], decorator_list=[], returns=None, lineno=23, col_offset=4),
        FunctionDef(name='load', args=arguments(args=[
            arg(arg='self', annotation=None, lineno=28, col_offset=13),
            arg(arg='path', annotation=None, lineno=28, col_offset=19),
          ], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]), body=[
            If(test=UnaryOp(op=Not(), operand=Call(func=Name(id='exists', ctx=Load(), lineno=29, col_offset=15), args=[
                Name(id='path', ctx=Load(), lineno=29, col_offset=22),
              ], keywords=[], lineno=29, col_offset=15), lineno=29, col_offset=11), body=[
                Raise(exc=Call(func=Name(id='OSError', ctx=Load(), lineno=29, col_offset=35), args=[
                    JoinedStr(values=[
                        FormattedValue(value=Name(id='path', ctx=Load(), lineno=29, col_offset=46), conversion=-1, format_spec=None, lineno=29, col_offset=43),
                        Str(s=' not found', lineno=29, col_offset=43),
                      ], lineno=29, col_offset=43),
                  ], keywords=[], lineno=29, col_offset=35), cause=None, lineno=29, col_offset=29),
              ], orelse=[], lineno=29, col_offset=8),
            Assign(targets=[
                Name(id='mod', ctx=Store(), lineno=30, col_offset=8),
              ], value=NameConstant(value=None, lineno=30, col_offset=14), lineno=30, col_offset=8),
            With(items=[
                withitem(context_expr=Call(func=Name(id='open', ctx=Load(), lineno=32, col_offset=13), args=[
                    Name(id='path', ctx=Load(), lineno=32, col_offset=18),
                  ], keywords=[], lineno=32, col_offset=13), optional_vars=Name(id='po', ctx=Store(), lineno=32, col_offset=27)),
              ], body=[
                Assign(targets=[
                    Name(id='mod', ctx=Store(), lineno=33, col_offset=12),
                  ], value=Call(func=Attribute(value=Name(id='po', ctx=Load(), lineno=33, col_offset=18), attr='read', ctx=Load(), lineno=33, col_offset=18), args=[], keywords=[], lineno=33, col_offset=18), lineno=33, col_offset=12),
                Try(body=[
                    Assign(targets=[
                        Name(id='mod', ctx=Store(), lineno=36, col_offset=16),
                      ], value=Call(func=Attribute(value=Name(id='self', ctx=Load(), lineno=36, col_offset=22), attr='parse', ctx=Load(), lineno=36, col_offset=22), args=[
                        Name(id='mod', ctx=Load(), lineno=36, col_offset=33),
                      ], keywords=[], lineno=36, col_offset=22), lineno=36, col_offset=16),
                  ], handlers=[
                    ExceptHandler(type=Name(id='Exception', ctx=Load(), lineno=38, col_offset=19), name='e', body=[
                        Expr(value=Call(func=Attribute(value=Name(id='tb', ctx=Load(), lineno=39, col_offset=16), attr='print_exc', ctx=Load(), lineno=39, col_offset=16), args=[], keywords=[], lineno=39, col_offset=16), lineno=39, col_offset=16),
                        Return(value=NameConstant(value=None, lineno=40, col_offset=23), lineno=40, col_offset=16),
                      ], lineno=38, col_offset=12),
                  ], orelse=[], finalbody=[], lineno=35, col_offset=12),
              ], lineno=32, col_offset=8),
            Return(value=Name(id='mod', ctx=Load(), lineno=41, col_offset=15), lineno=41, col_offset=8),
          ], decorator_list=[], returns=None, lineno=28, col_offset=4),
        FunctionDef(name='convert', args=arguments(args=[
            arg(arg='self', annotation=None, lineno=43, col_offset=16),
            arg(arg='tree', annotation=None, lineno=43, col_offset=22),
          ], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]), body=[
            Expr(value=Str(s='Convert a neu tree', lineno=44, col_offset=8), lineno=44, col_offset=8),
            Return(value=Call(func=Attribute(value=Name(id='self', ctx=Load(), lineno=45, col_offset=15), attr='traverse', ctx=Load(), lineno=45, col_offset=15), args=[
                Name(id='tree', ctx=Load(), lineno=45, col_offset=29),
              ], keywords=[], lineno=45, col_offset=15), lineno=45, col_offset=8),
          ], decorator_list=[], returns=None, lineno=43, col_offset=4),
        FunctionDef(name='traverse', args=arguments(args=[
            arg(arg='self', annotation=None, lineno=47, col_offset=17),
            arg(arg='tree', annotation=None, lineno=47, col_offset=23),
            arg(arg='proc', annotation=None, lineno=47, col_offset=29),
            arg(arg='c_it', annotation=None, lineno=47, col_offset=35),
          ], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[
            NameConstant(value=None, lineno=47, col_offset=40),
          ]), body=[
            Expr(value=Str(s='Traverse and process a tree', lineno=48, col_offset=8), lineno=48, col_offset=8),
            If(test=UnaryOp(op=Not(), operand=Name(id='c_it', ctx=Load(), lineno=49, col_offset=15), lineno=49, col_offset=11), body=[
                Assign(targets=[
                    Name(id='c_it', ctx=Store(), lineno=49, col_offset=21),
                  ], value=Lambda(args=arguments(args=[
                    arg(arg='t', annotation=None, lineno=49, col_offset=35),
                  ], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]), body=Subscript(value=Attribute(value=Name(id='t', ctx=Load(), lineno=49, col_offset=38), attr='tree', ctx=Load(), lineno=49, col_offset=38), slice=Index(value=Str(s='body', lineno=49, col_offset=45)), ctx=Load(), lineno=49, col_offset=38), lineno=49, col_offset=28), lineno=49, col_offset=21),
              ], orelse=[], lineno=49, col_offset=8),
            Assign(targets=[
                Name(id='result', ctx=Store(), lineno=50, col_offset=8),
              ], value=NameConstant(value=None, lineno=50, col_offset=17), lineno=50, col_offset=8),
            For(target=Name(id='c', ctx=Store(), lineno=52, col_offset=12), iter=Call(func=Name(id='c_it', ctx=Load(), lineno=52, col_offset=17), args=[
                Name(id='tree', ctx=Load(), lineno=52, col_offset=22),
              ], keywords=[], lineno=52, col_offset=17), body=[
                Expr(value=Call(func=Attribute(value=Name(id='self', ctx=Load(), lineno=53, col_offset=12), attr='traverse', ctx=Load(), lineno=53, col_offset=12), args=[
                    Name(id='c', ctx=Load(), lineno=53, col_offset=26),
                    Name(id='proc', ctx=Load(), lineno=53, col_offset=29),
                    Name(id='c_it', ctx=Load(), lineno=53, col_offset=35),
                  ], keywords=[], lineno=53, col_offset=12), lineno=53, col_offset=12),
              ], orelse=[], lineno=52, col_offset=8),
            Return(value=Name(id='result', ctx=Load(), lineno=54, col_offset=15), lineno=54, col_offset=8),
          ], decorator_list=[], returns=None, lineno=47, col_offset=4),
        FunctionDef(name='_parse', args=arguments(args=[
            arg(arg='self', annotation=None, lineno=56, col_offset=15),
            arg(arg='tree', annotation=None, lineno=56, col_offset=21),
          ], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]), body=[
            Expr(value=Str(s='Convert to module', lineno=57, col_offset=8), lineno=57, col_offset=8),
            Assign(targets=[
                Name(id='nodes', ctx=Store(), lineno=58, col_offset=8),
              ], value=List(elts=[], ctx=Load(), lineno=58, col_offset=16), lineno=58, col_offset=8),
            For(target=Name(id='n', ctx=Store(), lineno=60, col_offset=12), iter=Name(id='tree', ctx=Load(), lineno=60, col_offset=17), body=[
                Assign(targets=[
                    Name(id='head', ctx=Store(), lineno=61, col_offset=12),
                  ], value=Subscript(value=Name(id='n', ctx=Load(), lineno=61, col_offset=19), slice=Index(value=Str(s='head', lineno=61, col_offset=21)), ctx=Load(), lineno=61, col_offset=19), lineno=61, col_offset=12),
                Try(body=[
                    If(test=Call(func=Attribute(value=Name(id='self', ctx=Load(), lineno=64, col_offset=19), attr='is_expr', ctx=Load(), lineno=64, col_offset=19), args=[
                        Name(id='head', ctx=Load(), lineno=64, col_offset=32),
                      ], keywords=[], lineno=64, col_offset=19), body=[
                        Expr(value=Call(func=Attribute(value=Name(id='nodes', ctx=Load(), lineno=65, col_offset=20), attr='append', ctx=Load(), lineno=65, col_offset=20), args=[
                            Call(func=Name(id='parse', ctx=Load(), lineno=65, col_offset=33), args=[
                                Name(id='head', ctx=Load(), lineno=65, col_offset=39),
                              ], keywords=[], lineno=65, col_offset=33),
                          ], keywords=[], lineno=65, col_offset=20), lineno=65, col_offset=20),
                        Continue(lineno=66, col_offset=20),
                      ], orelse=[], lineno=64, col_offset=16),
                    If(test=Call(func=Attribute(value=Name(id='self', ctx=Load(), lineno=68, col_offset=19), attr='is_astir', ctx=Load(), lineno=68, col_offset=19), args=[
                        Name(id='head', ctx=Load(), lineno=68, col_offset=33),
                      ], keywords=[], lineno=68, col_offset=19), body=[
                        Expr(value=Call(func=Attribute(value=Name(id='nodes', ctx=Load(), lineno=69, col_offset=20), attr='append', ctx=Load(), lineno=69, col_offset=20), args=[
                            Call(func=Attribute(value=Attribute(value=Name(id='self', ctx=Load(), lineno=69, col_offset=33), attr='_astir', ctx=Load(), lineno=69, col_offset=33), attr='parse', ctx=Load(), lineno=69, col_offset=33), args=[
                                Name(id='n', ctx=Load(), lineno=69, col_offset=51),
                              ], keywords=[], lineno=69, col_offset=33),
                          ], keywords=[], lineno=69, col_offset=20), lineno=69, col_offset=20),
                        Continue(lineno=70, col_offset=20),
                      ], orelse=[], lineno=68, col_offset=16),
                    If(test=Call(func=Attribute(value=Name(id='self', ctx=Load(), lineno=72, col_offset=19), attr='is_nl', ctx=Load(), lineno=72, col_offset=19), args=[
                        Name(id='head', ctx=Load(), lineno=72, col_offset=30),
                      ], keywords=[], lineno=72, col_offset=19), body=[
                        Expr(value=Call(func=Attribute(value=Name(id='nodes', ctx=Load(), lineno=73, col_offset=20), attr='append', ctx=Load(), lineno=73, col_offset=20), args=[
                            Call(func=Attribute(value=Name(id='self', ctx=Load(), lineno=73, col_offset=33), attr='nl_to_ast', ctx=Load(), lineno=73, col_offset=33), args=[
                                Name(id='n', ctx=Load(), lineno=73, col_offset=48),
                              ], keywords=[], lineno=73, col_offset=33),
                          ], keywords=[], lineno=73, col_offset=20), lineno=73, col_offset=20),
                      ], orelse=[], lineno=72, col_offset=16),
                  ], handlers=[
                    ExceptHandler(type=Name(id='Exception', ctx=Load(), lineno=75, col_offset=19), name='e', body=[
                        Expr(value=Call(func=Attribute(value=Name(id='tb', ctx=Load(), lineno=76, col_offset=16), attr='print_exc', ctx=Load(), lineno=76, col_offset=16), args=[], keywords=[], lineno=76, col_offset=16), lineno=76, col_offset=16),
                        Expr(value=Call(func=Attribute(value=Name(id='pdb', ctx=Load(), lineno=77, col_offset=16), attr='post_mortem', ctx=Load(), lineno=77, col_offset=16), args=[], keywords=[], lineno=77, col_offset=16), lineno=77, col_offset=16),
                        Return(value=NameConstant(value=None, lineno=78, col_offset=23), lineno=78, col_offset=16),
                      ], lineno=75, col_offset=12),
                  ], orelse=[], finalbody=[], lineno=63, col_offset=12),
              ], orelse=[], lineno=60, col_offset=8),
            Assign(targets=[
                Name(id='module', ctx=Store(), lineno=79, col_offset=8),
              ], value=Call(func=Name(id='Module', ctx=Load(), lineno=79, col_offset=17), args=[
                Name(id='nodes', ctx=Load(), lineno=79, col_offset=24),
              ], keywords=[], lineno=79, col_offset=17), lineno=79, col_offset=8),
            Expr(value=Call(func=Attribute(value=Name(id='pdb', ctx=Load(), lineno=80, col_offset=8), attr='set_trace', ctx=Load(), lineno=80, col_offset=8), args=[], keywords=[], lineno=80, col_offset=8), lineno=80, col_offset=8),
            Expr(value=Call(func=Attribute(value=Name(id='self', ctx=Load(), lineno=81, col_offset=8), attr='fix_locations', ctx=Load(), lineno=81, col_offset=8), args=[
                Name(id='module', ctx=Load(), lineno=81, col_offset=27),
              ], keywords=[], lineno=81, col_offset=8), lineno=81, col_offset=8),
            Return(value=Name(id='module', ctx=Load(), lineno=82, col_offset=15), lineno=82, col_offset=8),
          ], decorator_list=[], returns=None, lineno=56, col_offset=4),
        FunctionDef(name='parse', args=arguments(args=[
            arg(arg='self', annotation=None, lineno=84, col_offset=14),
            arg(arg='text', annotation=None, lineno=84, col_offset=20),
          ], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]), body=[
            Assign(targets=[
                Name(id='ompo', ctx=Store(), lineno=85, col_offset=8),
              ], value=Call(func=Name(id='OMP', ctx=Load(), lineno=85, col_offset=15), args=[], keywords=[], lineno=85, col_offset=15), lineno=85, col_offset=8),
            Expr(value=Call(func=Attribute(value=Name(id='ompo', ctx=Load(), lineno=86, col_offset=8), attr='loads', ctx=Load(), lineno=86, col_offset=8), args=[
                Name(id='text', ctx=Load(), lineno=86, col_offset=19),
              ], keywords=[], lineno=86, col_offset=8), lineno=86, col_offset=8),
            Assign(targets=[
                Name(id='mod', ctx=Store(), lineno=88, col_offset=8),
              ], value=Call(func=Attribute(value=Name(id='self', ctx=Load(), lineno=88, col_offset=14), attr='_parse', ctx=Load(), lineno=88, col_offset=14), args=[
                Attribute(value=Name(id='ompo', ctx=Load(), lineno=88, col_offset=26), attr='tree', ctx=Load(), lineno=88, col_offset=26),
              ], keywords=[], lineno=88, col_offset=14), lineno=88, col_offset=8),
            Return(value=Name(id='mod', ctx=Load(), lineno=89, col_offset=15), lineno=89, col_offset=8),
          ], decorator_list=[], returns=None, lineno=84, col_offset=4),
        FunctionDef(name='is_expr', args=arguments(args=[
            arg(arg='self', annotation=None, lineno=91, col_offset=16),
            arg(arg='text', annotation=None, lineno=91, col_offset=22),
          ], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]), body=[
            Return(value=IfExp(test=Compare(left=Str(s=')', lineno=92, col_offset=23), ops=[
                In(),
              ], comparators=[
                Name(id='text', ctx=Load(), lineno=92, col_offset=30),
              ], lineno=92, col_offset=23), body=NameConstant(value=True, lineno=92, col_offset=15), orelse=NameConstant(value=False, lineno=92, col_offset=40), lineno=92, col_offset=15), lineno=92, col_offset=8),
          ], decorator_list=[], returns=None, lineno=91, col_offset=4),
        FunctionDef(name='is_astir', args=arguments(args=[
            arg(arg='self', annotation=None, lineno=94, col_offset=17),
            arg(arg='text', annotation=None, lineno=94, col_offset=23),
          ], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]), body=[
            Return(value=IfExp(test=Call(func=Attribute(value=Name(id='text', ctx=Load(), lineno=95, col_offset=23), attr='startswith', ctx=Load(), lineno=95, col_offset=23), args=[
                Str(s='air_', lineno=95, col_offset=39),
              ], keywords=[], lineno=95, col_offset=23), body=NameConstant(value=True, lineno=95, col_offset=15), orelse=NameConstant(value=False, lineno=95, col_offset=52), lineno=95, col_offset=15), lineno=95, col_offset=8),
          ], decorator_list=[], returns=None, lineno=94, col_offset=4),
        FunctionDef(name='is_nl', args=arguments(args=[
            arg(arg='self', annotation=None, lineno=97, col_offset=14),
            arg(arg='text', annotation=None, lineno=97, col_offset=20),
          ], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]), body=[
            Return(value=NameConstant(value=True, lineno=98, col_offset=15), lineno=98, col_offset=8),
          ], decorator_list=[], returns=None, lineno=97, col_offset=4),
        FunctionDef(name='nl_to_ast', args=arguments(args=[
            arg(arg='self', annotation=None, lineno=100, col_offset=18),
            arg(arg='text', annotation=None, lineno=100, col_offset=24),
          ], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]), body=[
            Return(value=None, lineno=101, col_offset=8),
          ], decorator_list=[], returns=None, lineno=100, col_offset=4),
        FunctionDef(name='fix_locations', args=arguments(args=[
            arg(arg='self', annotation=None, lineno=103, col_offset=22),
            arg(arg='node', annotation=None, lineno=103, col_offset=28),
          ], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]), body=[
            For(target=Name(id='n', ctx=Store(), lineno=105, col_offset=12), iter=Attribute(value=Name(id='node', ctx=Load(), lineno=105, col_offset=17), attr='body', ctx=Load(), lineno=105, col_offset=17), body=[
                Expr(value=Call(func=Name(id='fix_missing_locations', ctx=Load(), lineno=106, col_offset=12), args=[
                    Name(id='n', ctx=Load(), lineno=106, col_offset=34),
                  ], keywords=[], lineno=106, col_offset=12), lineno=106, col_offset=12),
              ], orelse=[], lineno=105, col_offset=8),
            Return(value=None, lineno=107, col_offset=8),
          ], decorator_list=[], returns=None, lineno=103, col_offset=4),
      ], decorator_list=[], lineno=16, col_offset=0),
    If(test=Compare(left=Name(id='__name__', ctx=Load(), lineno=110, col_offset=3), ops=[
        Eq(),
      ], comparators=[
        Str(s='__main__', lineno=110, col_offset=15),
      ], lineno=110, col_offset=3), body=[
        Import(names=[
            alias(name='sys', asname=None),
          ], lineno=111, col_offset=4),
        Assign(targets=[
            Name(id='neulang', ctx=Store(), lineno=112, col_offset=4),
          ], value=Call(func=Name(id='Neulang', ctx=Load(), lineno=112, col_offset=14), args=[], keywords=[], lineno=112, col_offset=14), lineno=112, col_offset=4),
        Expr(value=Call(func=Name(id='exec', ctx=Load(), lineno=113, col_offset=4), args=[
            Call(func=Name(id='compile', ctx=Load(), lineno=113, col_offset=9), args=[
                Call(func=Attribute(value=Name(id='neulang', ctx=Load(), lineno=113, col_offset=17), attr='load', ctx=Load(), lineno=113, col_offset=17), args=[
                    Subscript(value=Attribute(value=Name(id='sys', ctx=Load(), lineno=113, col_offset=30), attr='argv', ctx=Load(), lineno=113, col_offset=30), slice=Index(value=Num(n=1, lineno=113, col_offset=39)), ctx=Load(), lineno=113, col_offset=30),
                  ], keywords=[], lineno=113, col_offset=17),
                Str(s='<ast>', lineno=113, col_offset=44),
                Str(s='exec', lineno=113, col_offset=53),
              ], keywords=[], lineno=113, col_offset=9),
          ], keywords=[], lineno=113, col_offset=4), lineno=113, col_offset=4),
      ], orelse=[], lineno=110, col_offset=0),
  ])

