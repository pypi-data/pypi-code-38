
import inspect

def components (root, includes=['Model', 'Likelihood', 'Sampler']):
    """Auto-magically generate a table for all SPUX components."""

    traversed = []
    base = type(root).__bases__[0].__name__
    if base in includes:
        if hasattr (root, 'assign'):
            dependencies = list (inspect.signature (root.assign) .parameters.keys ())
            for arg in dependencies:
                option = getattr (root, arg)
                base = type(option).__bases__[0].__name__
                if hasattr (option, 'assign') or base in includes:
                    traversed += components (getattr (root, arg))
        component = {}
        component ['Component'] = type(root).__bases__[0].__name__
        component ['Class'] = type(root).__name__
        options = []
        args = list (inspect.signature (root.__init__) .parameters.keys ())
        for arg in args:
            value = str (getattr (root, arg))
            if len (value) > 10:
                value = '<...>'
            options += ['%s=%s' % (arg, value)]
        component ['Options'] = ', '.join (options)
        traversed += [component]
    return traversed

def infos (info):
    """Auto-magically generate a table for info tructure."""

    fields = list (info.keys ())
    if 'infos' in fields:
        taskinfos = info ['infos']
        if type (taskinfos) == list:
            iterators = '%s - %s' % (0, len (taskinfos) - 1)
            taskinfo = [taskinfo for taskinfo in taskinfos if taskinfo is not None] [0]
        elif type (taskinfos) == dict:
            iterators = sorted (list (taskinfos.keys ()))
            iterators = '%s - %s' % (iterators [0], iterators [-1])
            taskinfo = [taskinfo for taskinfo in taskinfos.values () if taskinfo is not None] [0]
        else:
            iterators = '-'
            taskinfo = taskinfos
        return [{'Fields' : ', '.join (fields), 'Iterators for infos' : iterators}] + infos (taskinfo)
    else:
        return [{'Fields' : ', '.join (fields), 'Iterators for infos' : '-'}]