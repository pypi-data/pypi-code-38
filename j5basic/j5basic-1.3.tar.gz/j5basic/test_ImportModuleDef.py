from j5basic import ImportModuleDef

def test_importmoduledef():
    module = {}
    ImportModuleDef.import_def_from('j5basic', module)
    assert 'ImportModuleDef' in module
    assert module['ImportModuleDef'] == ImportModuleDef
