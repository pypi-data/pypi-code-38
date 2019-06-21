
def get_all_baselines():

    baselines = dict()
    for baseline in Baseline.__subclasses__():
        b = baseline()
        baselines[b.name] = b
        
    return baselines

def get_all_baselines_by_type():

    baselines = dict()
    for baseline in Baseline.__subclasses__():        
        b = baseline()
        
        if b.baseline_type not in baselines:
            baselines[b.baseline_type] = []

        baselines[b.baseline_type].append(b.name)
        
    return baselines


def get_all_databases():

    databases = dict()
    for database in Databases.__subclasses__():
        d = database()
        databases[d.name] = d
        
    return databases
        

def get_config():
  """Returns a string containing the configuration information.
  """

  import bob.extension
  return bob.extension.get_config(__name__)


# gets sphinx autodoc done right - don't remove it
__all__ = [_ for _ in dir() if not _.startswith('_')]
