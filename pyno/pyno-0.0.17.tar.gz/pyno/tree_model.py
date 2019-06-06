

# todo generate type signatures for html elements with bootstrap classes for autocompletions as well
# todo update docs, defaults are acquired at definition time. Show trick for doing late bound attributes


import collections
from functools import partial
import inspect
from pyno.wsgi_interface import WSGIInterface
# todo, setup _before and _after defaults for elements, that include extra content from the defaults

def get_default_args(func):
    return {
        k: v.default
        for k, v in inspect.signature(func).parameters.items()
        if v.default is not inspect.Parameter.empty}

# todo, go through a thorough review to see if this function can replace the old get_default_args
def get_default_args_kwdefaults(func):
    deg = func.__kwdefaults__
    if deg is not None:
        return deg
    else:
        return {}

class ClassyMaker:
    """This is a wrapper class that provides the syntax H.div['class'] and H.div.class
    for defining a class while calling the element"""
    def __init__(self, node):
        self.node = node
        self.Class = []

    def __getattr__(self, item):
        self.Class.append(item)
        return self

    @property
    def _view(self):
        return self.node

    def __getitem__(self, item):
        self.Class.append(item)
        return self
    #  and hasattr(x, '__len__')
    def __call__(self, *args, **kwargs):

        class_str = ' '.join(x.replace('_', '-')
                                   for x in [*self.Class, kwargs.get('class'), kwargs.get('Class')]
                                   if x is not None and len(x)>1)

        return self.node(*args, **{k: v for k, v in kwargs.items() if k.lower() != 'class'},
                         **({'class':class_str} if class_str else {}))


class TreeNode(WSGIInterface):
    """tree_node is an object used to construct object-trees for generation of structed text like html/xhtml/svg code"""

    # defaults = {}  # Contains default values used for tag properties

    def __new__(typ, _tagname, *args, namespace='', Root=None, **kwargs):
        obj = object.__new__(typ)
        obj.namespace = namespace
        obj.name = _tagname
        obj.args = list(args)
        obj._before = []
        obj._after = []
        # The kwargs are initiated using defaults for the tag if they exist
        if Root is None:
            Root = HTML
        obj._before = Root.defaults.get(obj.name, {'_before':[]}).get('_before', [])
        obj._after = Root.defaults.get(obj.name, {'_after':[]}).get('_after', [])

        obj.kwargs = dict(Root.defaults[obj.name].copy(), **kwargs) if obj.name in Root.defaults else kwargs
        # todo perhaps given arguments should overwrite the defaults... otherwise they are more a sort of superfaults
        return obj

    def __getattr__(self, item):
        if item in object.__getattribute__(self, 'kwargs').keys():
            return self.kwargs[item]
        else:
            return object.__getattribute__(self, item)

    def __setattr__(self, key, value):
        if key not in ('name', 'args', 'kwargs', 'value', 'namespace', '_before', '_after'):
            self.kwargs[key] = value
        else:
            object.__setattr__(self, key, value)

    def __str__(self):
        return str(self.construct(*self.args, **self.kwargs))

    def construct(self, *args, **kwargs):
        """ This function constructs the output format. Here it's building a string representation of html"""
        # Properties with _ preceding are not passed on to html.
        property_args = {k: v for k, v in self.kwargs.items() if not k.startswith('_') and not (k == 'Class' and len(v.strip())==0)}

        # Generate attribute definitions:
        def value_exp(value):
            if value is None:
                return ''
            else:
                return f'="{value}"'
        properties = (' '+' '.join([f'{name.replace("_", "-")}{value_exp(value if name != "Class" else str(value).replace("_", "-"))}' for name, value in property_args.items()])) \
            if len(property_args) > 0 else ''

            # This raplaces iterators with lists so they aren't exhausted if the structure is iterated more than once.
        for n, elm in enumerate(self.args):
            if isinstance(elm, collections.abc.Iterator):
                self.args[n] = list(self.args[n])

        # Generate content string
        content_string = ''.join([''.join(str(x) for x in line) if hasattr(line, '__iter__')
                                  else str(line) for line in self._before + self.args + self._after])

        # Return content with enclosing tag
        if self.kwargs.get('_void_element', False):
            return f'<{self.namespace}{self.name}{properties} />'
        else:
            return f'<{self.namespace}{self.name}{properties}>{content_string}</{self.namespace}{self.name}>'





class NodeDispatcher(type):
    """ Diverts attributes to subclasses when they exist,
    and includes default arguments of construct in the initializer
    """
    def __getattr__(self, attr):
        for sub_node in HTML.__subclasses__():
            if sub_node.__name__ == attr:
                # todo adding default arguments cause 3x-4x slowdown
                return ClassyMaker(partial(sub_node, **get_default_args(sub_node.construct)))
                # return sub_node
        else:
            return ClassyMaker(partial(TreeNode, attr))


class HTML(TreeNode, metaclass=NodeDispatcher):  # type: HTMLTagList
    """ HTML is a class used to:
    * create TreeNodes though attribute dispatching     eg. H.div())
    * register user-defined tags through subclassing    eg. class myclass(H)
    * dispatch to user-defined classes though attribute dispatching eg. H.myclass()
    * Track default arguments to nodes eg. H.defaults['myclass'] = {'a': 3, 'b': 3}
    """

    @staticmethod
    def construct(func, **kwargs):
        """ This static method is a decorator that allows constructing subclass by decorating construct functions.
        This simplifies the main use case of construct-classes which is simply to wrap some structure without any class state or additional methods management"""
        globals()[func.__name__] = type(func.__name__, (HTML,), {"construct": lambda self, *args, **kwargs: func(*args, **kwargs)})
        return func

    defaults = {}

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, cls.__name__, *args, **kwargs)
    pass


class NodeDispatcherNS(type):
    """ Diverts attributes to subclasses when they exist,
    and includes default arguments of construct in the initializer
    """

    def __getattr__(self, attr):
        for sub_node in Namespace.__subclasses__():
            if sub_node.__name__ == attr:
                # todo adding default arguments cause 3x-4x slowdown
                return ClassyMaker(partial(sub_node, namespace=self._namespace, Root=self, **get_default_args(sub_node.construct)))
        else:
            return ClassyMaker(partial(TreeNode, attr, namespace=self._namespace, Root=self))


# todo is it still appropriate to use a metaclass pathway to attribute node generation considering the class suddenly has a namespace argument?

class Namespace(TreeNode, metaclass=NodeDispatcherNS):  # type: HTMLTagList
    """ HTML is a class used to:
    * create TreeNodes though attribute dispatching     eg. H.div())
    * register user-defined tags through subclassing    eg. class myclass(H)
    * dispatch to user-defined classes though attribute dispatching eg. H.myclass()
    * Track default arguments to nodes eg. H.defaults['myclass'] = {'a': 3, 'b': 3}
    """
    _namespace = ''
    defaults = {}

    @staticmethod
    def construct(func, **kwargs):
        """ This static method is a decorator that allows constructing subclass by decorating construct functions.
        This simplifies the main use case of construct-classes which is simply to wrap some structure without any class state or additional methods management"""
        globals()[func.__name__] = type(func.__name__, (HTML,), {"construct": lambda self, *args, **kwargs: func(*args, **kwargs)})
        return func


    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, cls.__name__, *args, **kwargs)
    pass



"""html is an instantiated object of the TreeSeed class, 
used to provide easy generation of TreeNodes through attribute access 
Type annotation against HTMLTagList is added purely to be able to have autocompletion in editors that support this"""
from pyno.html_tags_autocomplete import HTMLTagList
# Backwards compatibility
html = HTML  # type: HTMLTagList
TreeSub = HTML
