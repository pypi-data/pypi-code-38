import sys
import platform

from IPython.utils.capture import capture_output

def modules():
    names = sys.modules.keys()
    names = [name for name in names if not '.' in name]
    module_versions = {}
    for name in names:
        if hasattr(sys.modules[name], '__version__'):
            module_versions[name] = '{} (sys.modules)'.format(sys.modules[name].__version__)
    try:
        import pip
        pip_list = pip.operations.freeze.get_installed_distributions()  # @UndefinedVariable
        for entry in pip_list:
            (key, val) = entry.project_name, entry.version
            if key in module_versions:
                module_versions[key] += '; ' + val + '(pip)'
            else:
                module_versions[key] = val + '(pip)'
    except Exception:
        pass
    try:
        import conda.cli
        with capture_output() as c:
            conda.cli.main('list','--export')
        conda_list = c.stdout
        for entry in conda_list.splitlines():
            a = entry.split('=')
            if len(a)<2:
                continue
            key,val = a[:2]
            if key in module_versions:
                module_versions[key] +='; ' + val + '(conda)'
            else:
                module_versions[key] = val+ '(conda)'
    except Exception:
        pass
    return module_versions

def hardware():
    system_info = '; '.join([platform.platform(), platform.python_implementation() + ' ' + platform.python_version()])
    try:
        import psutil
        system_info += '; ' + str(psutil.cpu_count(logical=False)) + ' cores'
        system_info += '; ' + str(float(psutil.virtual_memory().total) / 2 ** 30) + ' GiB'
    except:
        pass
    return system_info
