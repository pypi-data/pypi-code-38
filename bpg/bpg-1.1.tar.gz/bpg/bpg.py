import os
import yaml
import yamlordereddictloader

'''
in-memory repository of templates. The templates are 
accessible by name. 
The templates are loaded into this repository from
local file system. The environment variable 
BPG_TEMPLATES_DIR specifies the owning directory
of *.yml template files. 
'''
ENV_VAR_TEMPLATE_REPO = 'TEMPLATES_DIR'
class TemplateLibrary(object):
    def __init__(self, repo_url=None):
        # key: template name
        # value: ordered dict of version->template
        #        sorted by version key
        self.repo = {}
        if repo_url is None:
            if not ENV_VAR_TEMPLATE_REPO in os.environ:
                raise ValueError('''WARN: no templates directory. 
                No templates would be available.
                Set environment variable [{0}]'''.format(ENV_VAR_TEMPLATE_REPO))
            else:
                templates_dir =  os.environ[ENV_VAR_TEMPLATE_REPO]
        else: 
            templates_dir = repo_url
        print 'loading templates from {0}'.format(repo_url)
        templates = YAMLTemplateLoader().load(templates_dir)
        for t in templates:
            self.add_template(t)
            
    def __len__(self):
        return len(self.repo)
    
    def add_template(self, t):
        print 'add template {0} to library'.format(t)
        name = t.name.upper()
        templates = self.repo.get(name,{})
        templates[t.version] = t
        self.repo[name] = templates
        
    '''
    finds the template of given name
    Template names are case-insensitive
    '''
    def find_template(self, name, version=None):
        '''
        @param name: name of a template. case-insensitive 
        @param version: if not present, latest version is used 
        '''
        if name.upper() not in self.repo:
            raise ValueError('{0} not found in known templates {1}'.format(name, self.repo.keys()))
        templates = self.repo[name.upper()]
        if version:
            if version in templates:
                return templates[version]
        else:
            templates.keys().sort()
            latest = templates.keys()[0]
            return templates[latest]
    
    def get_template_names(self):
        '''
        get all template names in this repository
        '''
        return self.repo.keys()
    
    def get_template_vesrions(self, name):
        '''
        gets all versions of named template
        '''
        if name.upper() not in self.repo:
            raise ValueError('{0} not found in known templates {1}'.format(name, self.repo.keys()))
        templates = self.repo[name.upper()]
        return [t.version for t in templates.values()]

        
'''
A template is a definition for configurable parameters.
The configurable parameter definitions in a template
can specify an expression, for example, 
    log_disk_size = {% percentage % database_size %}
instead of a constant:
    log_disk_size = 50GB
    
An expression is denoted by enclosing in {% %} markers.

A template can be loaded from a YAML file.
---
name: test
display-name: a template for testing
version: 1.0.0
a: 
   name: A constant property
   display-name:
   description:
   version:
   value: 1234
b: 
   name: An expression property
   display-name:
   description:
   version:
   value: '{% x + y %}'
templates:
   sub-template1: 
      ....
   sub-template2: 
      ....
      
---
    
A template can nest one or more (sub)templates
via 'templates' property.

A template is a factory for configuration (which is a 
hierarchical key-value pairs such as JSON). A set 
a set of variables must be supplied 
to evaluate an expression.
 
@author: pinaki.poddar
'''
import copy

TEMPLATES='templates'
REQUIRES ='requires'
VALUE='value'
class Template(object):
    def __init__(self, data={}):
        '''
          creates a template with given dictionary
          
          @param: dictionary value can be an expression.
        '''
        self.data = copy.deepcopy(data)
        if 'name' in self.data:
            raise ValueError('no name for template')
        self.name = self.data.get('name')
        self.version = self.data.get('version', '')
        self.loc  = None
        
    def is_special_property(self, key):
        return key in ['name', 'requires', 'version']
        
    def load(self, filename):
        '''
          loads template from given YAML file 
        '''
        with open(filename, 'r') as f:
            self.data = yaml.load(f,Loader=yamlordereddictloader.Loader) 
            if 'name' in self.data:
                self.name = self.data['name']
            else:
                raise ValueError('No name for template')
            self.loc = f.name 
            
    def instantiate(self, variables={}, ctx=None):
        '''
           instantiates this template to create a configuration.
           expressions are evaluated with given variables
           
           @param: variables dictionary of variable 
           name and value. If a variable is missing,
           an exception is raised
           @return:  configuration has same keys.
           All expressions, however, 
           are evaluated by substituting given variables.
           A template field is a dictionary describing
           property metadata. The instantiated configuration
           is a set of key-value pairs.
        '''        
        conf = {}
        for k,v in self.data.iteritems():
            if self.is_special_property(k): continue
            if (k == TEMPLATES): # sub-templates
                for subk, subv in v.iteritems():
                    print 'instantiate sub-template {0}'.format(subk)
                    sub_template = Template(subv)
                    conf[subk] = sub_template.instantiate(variables, ctx)
                    print 'instantiated sub-template {0} to {1}'.format(subk, conf[subk])
                    variables.update(conf)  
                    print 'updated variables with {0} to {1}'.format(subk, variables)
            else: # property definitions
                if isinstance(v, basestring) or isinstance(v, int) or isinstance(v, bool):
                    value = v
                elif not VALUE in v:
                    raise ValueError('''property [' + {0} + '] definition has no value'
                        Its value type is {1}'''.format(k, type(v)))
                else: 
                    value = v[VALUE]
                    exp = self.parseExpression(value)
                    if exp:
                        try:
                            print 'evaluate [{0}] with variables [{1}]'.format(exp, variables)
                            conf[k] = eval(exp, None, variables)
                            variables.update({k:conf[k]})  # dependent variable
    #                         print 'evaluated [{0}] to [{1}]'.format(k, conf[k])
    #                         print 'updated variables {0}'.format(variables)
                            
                        except NameError as err:
                            raise ValueError('''expression for {0}=[{1}] uses undefined variable.
                            available variables are {2}:'''.format(k,exp, variables), err)    
                        except Exception as err:
                            raise ValueError('can not evaluate ' + exp, err)
                    else:
                        # literal
                        conf[k] = value
                        variables.update({k:value})  # dependent variable
                        print 'updated variables with constant value for {0} to {1}'.format(k, variables)

        return conf 
             
    def get_variables(self):
        '''
            get variables declared for this template and
            all sub-templates
            @return: list of variable names
        '''
        varibles = self.data[REQUIRES] if REQUIRES in self.data else []
        for k,v in self.data.iteritems():
            if (k == 'templates'): # sub-templates
                for subk, subv in v.iteritems():
                    if 'requires' in subv:
                        varibles.append(subv['requires'])
        return varibles
    
    def parseExpression(self, s): 
        '''
        parses given string to an expression
        @return None if not an expression. 
        An expression is enclosed in {% %} markers 
        '''
        if (not isinstance(s, basestring)): return None  
        if (not s.startswith('{%')): return False
        if (not s.endswith('%}')): return False
        return s[2:-2]
            
        
    def __getitem__(self, key):
        return self.find(key)
    
    def find(self, path):
        '''
        finds a nested property of a sub-template
        by given path
        @param path: a dot-separated sequence of key
        to a nested property/sub-template
        '''
        keys = path.split('.')
        rv = self.data
        for key in keys:
            if (not key in rv):
                if TEMPLATES in rv: 
                    rv = rv['templates']
                else:
                    raise ValueError('segment [{0}] in path [{1}] not found'.format(key, path))
            rv = rv[key]
        return rv

    def __str__(self):
        return '{0} (v{1}) ({2})'.format(self.name, self.version, self.loc) 
    
class YAMLTemplateLoader(object):
    def load(self, path):
        print 'loading templates from all *.yml found under [{0}] directory'.format(path)
        templates = []
        for r,d,files in os.walk(path):
            for f in files:
                if f.endswith('.yml'):
                    t = Template()
                    t.load(os.path.join(r,f))
                    templates.append(t)
        print 'loaded {0} templates {1}'.format(
            len(templates),[t.name for t in templates])
        return templates


import re
VERSION_REGEX=r'(?P<major>\d+)\.(?P<minor>\d+)(\.(?P<patch>\d+))?'
class Version(object):
    '''
        follows syntax of semantic version
    '''
    def __init__(self, s):
        m = re.match(VERSION_REGEX, s)
        if not m:
            raise ValueError('invalid semantic version {0}'.format(s))
        self.major = int(m.group('major'))
        self.minor = int(m.group('minor'))
        try:
            self.patch = int(m.group('patch'))
        except Exception:
            self.patch = None
        
    def __cmp__(self, other):
        if (not isinstance(other, Version)) :
            return -1
        if self.major > other.major: 
            return 1
        elif other.major > self.major:
            return -1
        else: 
            if self.minor > other.minor:
                return 1
            elif other.minor > self.minor:
                return -1
            else:
                return 0
        
    def __str__(self):
        if self.patch:
            return '{0}.{1}.{2}'.format(self.major, self.minor, self.patch) 
        else:
            return '{0}.{1}'.format(self.major, self.minor) 
