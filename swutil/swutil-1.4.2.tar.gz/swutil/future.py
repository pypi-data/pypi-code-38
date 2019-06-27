from __future__ import annotations
import importlib
import copy
import inspect
import ast

HIDDENKEY = "__graphexecutehiddenreturn__"

class nt:
    def __init__(self,**kwargs):
        for kw in kwargs:
            self.__dict__[kw] = kwargs[kw]

class graphexecute:
    def __init__(self,fun=None,**opts):
        self.opts = {'verbose':False}
        self.opts.update(opts)
        if fun:
            self.parts = self.get_parts(fun)
        self.fun = fun

    def __call__(self,*args,**kwargs):
        if self.fun:
            return self.execute(*args,**kwargs)
        else:
            self.fun = args[0]
            self.parts = self.get_parts(self.fun)
            return self

    def execute(self,*args,**kwargs):
        variables = kwargs
        parts = self.parts.copy()
        while parts:
            part_name = self.find_next_part(parts, variables)
            part = parts[part_name]
            args = {par:variables[par] for par in part.parameters}
            if self.opts['verbose']:
                print('Executing part '+part_name)
            returned = part.fun(**args)
            del parts[part_name]
            try:
                returned = returned[HIDDENKEY]
                for par in part.parameters:
                    if par in returned:
                        variables[par] = returned[par]
                    else:
                        del variables[par]
                for par in part.returns:
                    if par in returned:
                        variables[par] = returned[par]
            except (TypeError,KeyError,IndexError):
                return returned

    @staticmethod
    def get_parts(f):
        source = inspect.getsource(f)
        signature = source.split('\n',1)[0]
        msource = inspect.getsource(importlib.import_module(f.__module__))
        for i,line in enumerate(msource.splitlines()):
            if line == signature:
                break
        else:
            i=0
        source = '\n'*i+source
        tree = ast.parse(source)
        parts = tree.body[0].body
        if not all(isinstance(part,ast.FunctionDef) for part in parts):
            raise Exception(f'All parts of the algorithm {f.__name__} must be wrapped in functions')
        functions = {}
        suffix='return {"'+HIDDENKEY+'":locals()}'
        for part in parts:
            if part.returns:
                if hasattr(part.returns,'elts'):
                    returns = [elt.id for elt in part.returns.elts]
                else:
                    returns = [part.returns.id]
                prefix = ''.join([ret+'=' for ret in returns])+'None'
            else:
                prefix = 'pass'
            parameters = [arg.arg for arg in part.args.args]
            mod_tree = copy.deepcopy(tree)
            new_body = [ast.parse(prefix).body[0],
                    *part.body,
                    ast.parse(suffix).body[0]]
            part.body = new_body
            mod_tree.body = [part]
            code = compile(mod_tree,f.__code__.co_filename,'exec')
            namespace={}
            namespace.update(importlib.import_module(f.__module__).__dict__)
            exec(code,namespace)
            functions[part.name] = nt()
            functions[part.name].fun = namespace[part.name]
            functions[part.name].returns = returns
            functions[part.name].parameters = parameters
        return functions

    @staticmethod
    def find_next_part(parts,variables):
        for part_name in parts:
            if all(par in variables for par in parts[part_name].parameters):
                return part_name
        else:
            print(parts,variables)
            raise Exception('None of the remaining parts ('+','.join(parts.keys())+') can be executed')
