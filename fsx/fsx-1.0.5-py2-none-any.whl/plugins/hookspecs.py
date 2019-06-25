import pluggy

hookimpl = pluggy.HookimplMarker('fsx')
hookspec = pluggy.HookspecMarker('fsx')

@hookspec
def fsx_get_module_dict():
    ''' Returns a dict like `{<<module_name>>: <<module>>}`. '''
    pass


@hookspec
def fsx_get_fake_module_dict(fsx_fake_tree):
    ''' Returns a dict like `{<<module_name>>: <<fake_module>>}`. '''
    pass


