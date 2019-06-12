
# import inspect

# def auto (root, components):
#     """Auto-magically assign all SPUX components to each other if possible."""

#     # WORK IN PROGRESS

#     bases = {type(component).__bases__[0].__name__ : [] for component in components}
#     for index, (label, component) in enumerate (components.items()):
#         base = type(component).__bases__[0].__name__.lower()
#         bases [base] += [{'index' : index, 'label' : label, 'name' : component.name}]
#     if hasattr (root, 'assign'):
#         argspec = inspect.getargspec (root.assign)
#         args = argspec.args [1:]
#         vals = argspec.defaults [1:]
#         for arg, val in zip (args, vals):
#             if arg in components.keys () or (arg == 'likelihood' and 'replicates' in components.keys ()):
#                 auto (, components)


#     # TODO: error message and sys.exit() if auto-assignment failed - an advice to check for duplicate components or to perform the assignments manually instead

#     # TODO: dumper.config here instead of in the component.assign

#     return root