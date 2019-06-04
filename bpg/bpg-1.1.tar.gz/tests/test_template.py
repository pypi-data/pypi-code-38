from bpg.bpg import Template,TemplateLibrary
import pytest

lib = TemplateLibrary('templates')

def testTemplatesAreLoaded():
    assert len(lib) > 0


def testTemplateExpressionsAreEvaluted():
    desc = {'a':{'value':52}, 
            'b':{'value':'axds'}, 
            'formula':{'value':'{% x*y %}'}}
    template = Template(desc)
    
    conf = template.instantiate({'x':10, 'y':25});
    assert 'formula' in conf
    assert conf['formula'] == 10*25
    
def test_templateConstants():
    desc = {
        'a':{'value':52}, 
        'c':{'value':'axds'}
    }
    template = Template(desc)
    conf = template.instantiate();
    assert conf['a'] == 52
    
def test_templateNested():
    desc = {'a':{'value':52}, 
            'templates':{
                'nested':{'c':{'value':'{%x+y%}'}}
            }}
    template = Template(desc)
    
    conf = template.instantiate({'x':10, 'y':25});
    assert conf['nested']['c'] == 10 + 25
    
def test_templateStringConcatenation():
    desc = {'formula':{'value':'{% x+y %}'}}
    template = Template(desc)
    
    conf = template.instantiate({'x':'this', 'y':' is a test'});
    assert conf['formula'] == 'this is a test'

def test_templateMissingVaraible():
    desc = {'a':{'value':52}, 
            'c':{'value':'axds'}, 
            'formula':{'value':'{% x*y*z %}'}}
    template = Template(desc)
    with pytest.raises(ValueError) as e:
        conf = template.instantiate({'x':50, 'y':12});
    assert 'undefined variable' in str(e)
    assert '\'z\' is not defined' in str(e)
    
def testLoadTemplate():
    template = lib.find_template('test')
    conf = template.instantiate({'x':10, 'y':25});
    assert conf['formula'] == 10*25
    
def testFindSimpleProperty():
    template = lib.find_template('test')
    assert template
    assert 'expression' in template.find('display-name') 
    assert 'expression' in template['display-name']
    
    formula = template.find('formula')
    assert formula
    assert formula['value'] == '{% x*y %}'
    
def testFindNestedProperty():
    template = lib.find_template('test')
    p = template.find('section1.a')
    assert p
    assert p['value'] == 42

def testFindTemplateByName():
    assert lib.find_template("test") is not None
    
def testUnknownTemplate():
    with pytest.raises(ValueError) as e:
        lib.find_template("unknown") 
        
def testSQLServerTemplate(): 
    template = lib.find_template('sqlserver')
    variables = {'database_size': 10000}
    conf = template.instantiate(variables)
    
#    initial_size = "{% database_size *  count %}"
    assert conf['data_files']['initial_size'] == 10000 * 4

    assert conf['data_disks']['size'] == 1.2 * (2 * 10000 * 4)
#    1.2 * data_files['max_size']
#    data_files['max_size'] = 2 * initial_size
# 


def testDependentFormula(): 
    template = lib.find_template('test')
    variables = {'x':10, 'y':5}
    conf = template.instantiate(variables)
    
    assert conf['formula'] == 10*5
    assert conf['dependent-formula'] == 10*5*2
    
def testLibrary():
    pass