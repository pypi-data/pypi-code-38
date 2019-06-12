import pandas as pd
import pkg_resources

def _load_from_resource(resource_path):
    return pd.read_csv(pkg_resources.resource_filename(__name__,resource_path))

def load_beauty():
    resource_path = '/'.join(('data','beauty.zip'))
    return _load_from_resource(resource_path)

def load_starbucks():
    resource_path = '/'.join(('data','starbucks.zip'))
    return _load_from_resource(resource_path) 

def load_bond():
    resource_path = '/'.join(('data','bond.zip'))
    return _load_from_resource(resource_path) 


def load_movies():
    resource_path = '/'.join(('data','movies.zip'))
    return _load_from_resource(resource_path) 


def load_chopsticks():
    resource_path = '/'.join(('data','chopsticks.zip'))
    return _load_from_resource(resource_path) 


def load_chopsticks_full():
    resource_path = '/'.join(('data','chopsticks_full.zip'))
    return _load_from_resource(resource_path) 


def load_correlation_example():
    resource_path = '/'.join(('data','correlation.zip'))
    return _load_from_resource(resource_path) 

def load_titanic():
    resource_path = '/'.join(('data','titanic.zip'))
    return _load_from_resource(resource_path) 

def load_head_size():
    resource_path = '/'.join(('data','head_size.zip'))
    return _load_from_resource(resource_path) 


