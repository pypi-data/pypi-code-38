# Treep, copyright 2019 Max Planck Gesellschaft
# Author : Vincent Berenz 

# This file is part of Treep.

#    Treep is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    Treep is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with Treep.  If not, see <https://www.gnu.org/licenses/>.


import os
import yaml
from collections import OrderedDict

from .repository import Repository
from .project import Project
from .projects import Projects
from .configuration import Configuration
from .exceptions import TreepConfigFolderNotFound
from .compiler import Compiler

from . import repository


CONFIG_FOLDER_PREFIX = "treep_"
REPOSITORIES_PATTERN = "repositories"
PROJECTS_PATTERN = "projects"
CONFIGURATION_PATTERN = "configuration"


def _find_root(starting_dir=None):

    def _found(path):
        global CONFIG_FOLDER_PREFIX
        files  = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
        treep_folders = [f for f in files if f.startswith(CONFIG_FOLDER_PREFIX)]
        if len(treep_folders)==0 :
            return None
        return treep_folders
        
    if starting_dir is None:
        starting_dir = os.getcwd()

    current_dir = starting_dir

    config_folders = _found(current_dir)
    while not config_folders:
        try :
            current_dir = os.path.abspath(current_dir+os.sep+"..")
            if current_dir == "/":
                return None,None
            config_folders = _found(current_dir)
        except:
            return None,None

    return current_dir,config_folders


def _relative_to_absolute_path(path):

    global REPOSITORIES_FILE
    starting_path = os.getcwd()
    root,_ = _find_root(REPOSITORIES_FILE)
    if root is None:
        raise Exception("failed to find treep root containing "+starting_path)
    return os.path.abspath(root+os.sep+path)


def _get_workspace_path():

    root,_ = _find_root()
    return root+os.sep+"workspace"+os.sep


def _yaml_to_repositories(yaml_content,configuration):

    valid_keys = ['origin','path','branch','commit','tag',
                  'compilation']

    repositories = []

    for repository,value in yaml_content.items():

        for key in value.keys():
            if key not in valid_keys:
                raise Exception('invalid key for repository '+repository+": "+key)
        
        try :
            path = value['path']
        except :
            raise Exception("failed to find path for repository "+repository)

        try :
            origin = value['origin']
            origin = configuration.get_origin(repository,origin)
        except Exception as e:
            origin = configuration.get_origin(repository,None)

        try :
            branch = value['branch']
        except :
            branch = 'master'

        try :
            commit = value['commit']
        except :
            commit = None

        try :
            tag = value['tag']
        except :
            tag = None

        try:
            compilation = value['compilation']
        except:
            compilation = None
            
        repositories.append( Repository ( repository,
                                          origin,
                                          path,
                                          branch=branch,
                                          commit=commit,
                                          tag=tag,
                                          compilation=compilation) )
        
    return repositories

        
def _yaml_to_configuration(yaml_content,compiler):

    origin_prefixes = {}
    
    valid_fields = ["origin_prefixes","compilation"]

    for field in yaml_content:

        if field not in valid_fields:
            raise Exception("invalid field in treep configuration yaml file: "+str(field))

        if field == "origin_prefixes":

            origin_prefixes = yaml_content[field]

        if field == "compilation":

            tags = yaml_content[field]

            for tag,labels in tags.items():

                try :
                    category = Compiler.YAML_TAGS[tag]
                except :
                    error = "invalid compilation tag in treep configuration yaml file: "+str(tag)
                    error += "\nvalid tags: "+", ".join(Compiler.YAML_TAGS.keys())
                    raise Exception(error)

                for label,kwargs in labels.items():
                    if label=="default":
                        compiler.add(tag,category,kwargs)
                    else:
                        compiler.add(label,category,kwargs)
                
            
    return Configuration(origin_prefixes)

    
def _yaml_to_projects(yaml_content):

    valid_keys = ['repos','parent_projects']
    
    projects = []

    for project in yaml_content:
        
        for key in yaml_content[project].keys():
            if key not in valid_keys:
                raise Exception('invalid key for project '+project+": "+key)
        
        try :
            repos = yaml_content[project]['repos']
        except :
            repos = []

        try :
            parent_projects = yaml_content[project]['parent_projects']
        except :
            parent_projects = []
            
        projects.append( Project( project,
                                  parent_projects,
                                  repos) )

    return projects



def _read_yaml_file(abs_path):

    # credit:
    # https://stackoverflow.com/questions/5121931/in-python-how-can-you-load-yaml-mappings-as-ordereddicts
    def ordered_load(stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict):
            class OrderedLoader(Loader):
                pass
            def construct_mapping(loader, node):
                loader.flatten_mapping(node)
                return object_pairs_hook(loader.construct_pairs(node))
            OrderedLoader.add_constructor(
                yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
                construct_mapping)
            return yaml.load(stream, OrderedLoader)
                                            
    
    try :
        with open(abs_path,"r") as f:
            content = f.readlines()
    except Exception as e:
        raise Exception("failed to read file content "+abs_path+": "+str(e))

    try :
        content = ordered_load("\n".join(content),Loader=yaml.SafeLoader)
    except Exception as e:
        raise Exception("failed to parse yaml file "+abs_path+": "+str(e))

    return content


def _get_files(folder,pattern):

    files  = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    files = [f for f in files if pattern in f]
    files = [f for f in files if f.endswith(".yaml")]
    
    return [folder+os.sep+f for f in files]
    

def _read_configuration_file(path,compiler):

    yaml_content = _read_yaml_file(path)
    if yaml_content is None:
        configuration = Configuration({})
    else:
        configuration = _yaml_to_configuration(yaml_content,compiler)
    return configuration


def _read_configuration_files(configuration_folder,compiler):

    global CONFIGURATION_PATTERN

    configuration_files = _get_files(configuration_folder,CONFIGURATION_PATTERN)

    total_configuration = Configuration({})

    for configuration_file in configuration_files:
        configuration = _read_configuration_file(configuration_file,compiler)
        total_configuration.extend(configuration)

    return total_configuration


def _read_repositories_file(path,configuration):

    yaml_content = _read_yaml_file(path)
    repositories = _yaml_to_repositories(yaml_content,configuration)
    return repositories


def _read_repositories_files(configuration_folder,configuration):

    global REPOSITORIES_PATTERN

    repositories_files = _get_files(configuration_folder,REPOSITORIES_PATTERN)

    all_repositories = []
    
    for repositories_file in repositories_files:
        yaml_content = _read_yaml_file(repositories_file)
        repositories = _yaml_to_repositories(yaml_content,configuration)
        all_repositories.extend(repositories)
        
    return all_repositories


def _read_projects_file(path):

    yaml_content = _read_yaml_file(path)
    projects = _yaml_to_projects(yaml_content)
    return projects


def _read_projects_files(configuration_folder):

    global PROJECTS_PATTERN

    projects_files = _get_files(configuration_folder,PROJECTS_PATTERN)
    
    all_projects = []

    for project_file in projects_files:
        projects = _read_projects_file(project_file)
        all_projects.extend(projects)

    return all_projects


def _check_projects_composed_of_existing_repositories(projects,repositories):

    repo_names = repositories.keys()

    for project in projects.values():
        for repo in project.repositories:
            if repo not in repo_names:
                raise Exception("project "+project.name+" contains an unknown repository: "+repo)


def _read_compilation_script(path):
    items = os.listdir(path)
    if "compilation.py" not in items:
        return None
    return path+os.sep+"compilation.py"
    
    
def read_configuration_files():

    all_projects = {}
    all_repositories = {}

    root,configuration_folders = _find_root()

    if configuration_folders is None:
        raise TreepConfigFolderNotFound()
    
    all_projects = {}
    all_repositories = {}
    ordered_repositories = []

    # object for tracking which compilation method
    # are supported (e.g. catkin, cmake, pip)
    compiler = Compiler()
    
    # reading all configuration folders, one by one
    for configuration_folder in configuration_folders :

        abs_path = root+os.sep+configuration_folder
        
        # compilation folder may contain a file "compilation.py" which
        # contains user taylored compilation script generating functions
        compilation_script = _read_compilation_script(abs_path)
        if compilation_script is not None:
            compiler.add_compilation_script(compilation_script)
        
        configuration = _read_configuration_files(abs_path,compiler)
        repositories = _read_repositories_files(abs_path,configuration)
        # keeping the order in which repositories were declared in the yaml file
        ordered_repositories.extend([repo for repo in repositories])
        projects = _read_projects_files(abs_path)
        
        repositories = {r.name : r for r in repositories}
        projects = {p.name : p for p in projects}

        all_repositories[configuration_folder]=repositories
        all_projects[configuration_folder]=projects

        
    def _conflicts(config_folder_dict):
        keys_folder = {}
        for folder,dict_ in config_folder_dict.items():
            for key in dict_.keys():
                try :
                    keys_folder[key].append(folder)
                except:
                    keys_folder[key]=[folder]
        r = {key:value for key,value in keys_folder.items() if len(value)>1}
        return r
        
    # where some repositories/projects defined in more than one configuration folder ?
    # nothing solved, but keeping the trace of this
    conflicts_repositories = _conflicts(all_repositories)
    conflicts_projects = _conflicts(all_projects)

    def _merge(config_folder_dict):

        def _merge_dicts(d1,d2):
            for k,v in d2.items():
                d1[k]=v
            return d1

        r = {}

        for d in config_folder_dict.values():
            r = _merge_dicts(r,d)

        return r

    # merging all configurations into one. If conflicts, only
    # one version of the repositories/projects is arbitrary kept
    all_repositories = _merge(all_repositories)
    all_projects = _merge(all_projects)

    
    # sanity check on projects: no unknown repository used in projects ?
    # DEPRECATED: maybe the repos are from another treep_xxx configuration folder
    #             which the user of a particular project may need to get separately
    #_check_projects_composed_of_existing_repositories(all_projects,all_repositories)
    
    workspace_path = _get_workspace_path()

    projects_ = Projects(all_projects,
                         all_repositories,
                         ordered_repositories,
                         compiler,
                         workspace_path,
                         conflicts_repositories,
                         conflicts_projects)

    return projects_
        


def generate_yaml_configuration_files(path,statuses,
                                      project_name="PROJECT",
                                      commit=False):


    def get_relative_path(abs_path):
        index_workspace = abs_path.index("workspace")
        return abs_path[index_workspace+10:]
    
    # annoyed I need to write the yaml file "manually", but
    # pyyaml throws a "NoneType" exception

    file_repos = path+os.sep+'treep_repositories.generated'
    
    with open(file_repos, 'w+') as f:

        for status in statuses:

            f.write(status.repo_name+":\n")
            f.write("    path: "+get_relative_path(status.path)+"\n")
            f.write("    origin: "+str(status.origin)+"\n")
            f.write("    branch: "+status.branch+"\n")

            if commit:
                f.write("    commit: "+status.commit+"\n")

            if commit:
                values['commit'] = status.commit

                content_repositories[status.repo_name] = values

    file_projects = path+os.sep+'treep_projects.generated'
        
    with open(file_projects, 'w+') as f:

        f.write(project_name+":\n")
        f.write("    repos: "+repr([status.repo_name for status in statuses]))

    
    return file_repos,file_projects
