import copy
import os
import tempfile
import yaml
from zalando_kubectl.utils import auth_token

KUBECONFIG = os.path.expanduser('~/.kube/config')
KUBE_USER = 'zalando-token'


def update(url, alias):
    token = auth_token()
    name = alias or generate_name(url)
    new_config = {
        'apiVersion': 'v1',
        'kind': 'Config',
        'clusters': [{'name': name, 'cluster': {'server': url}}],
        'users': [{'name': KUBE_USER, 'user': {'token': token}}],
        'contexts': [{'name': name, 'context': {'cluster': name, 'user': KUBE_USER}}],
        'current-context': name
    }
    config = read_config()
    updated_config = merge_config(config, new_config)
    if updated_config != config:
        write_config(updated_config)
    return updated_config


def update_token():
    token = auth_token()

    config_parts = {
        'users': [{'name': KUBE_USER, 'user': {'token': token}}]
    }
    config = read_config()
    updated_config = merge_config(config, config_parts)
    # Migrate old user names to new name
    for context in updated_config.get('contexts', []):
        if 'zalan_do' in context.get('context', {}).get('user', ''):
            context['context']['user'] = KUBE_USER

    if updated_config != config:
        write_config(updated_config)
    return updated_config


def write_config(config):
    os.makedirs(os.path.dirname(KUBECONFIG), exist_ok=True)
    new_fp, new_file = tempfile.mkstemp(prefix="config", dir=os.path.dirname(KUBECONFIG))
    try:
        with open(new_fp, mode="w", closefd=True) as f:
            yaml.safe_dump(config, f)
            f.flush()
    except Exception:
        os.unlink(new_file)
        raise
    else:
        os.rename(new_file, KUBECONFIG)


def generate_name(url):
    url = url.replace('http://', '')
    url = url.replace('https://', '')
    url = url.replace('.', '_')
    url = url.replace('/', '')
    return url


def read_config():
    try:
        with open(KUBECONFIG, 'r') as fd:
            data = yaml.safe_load(fd)
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    return {}


def merge_config(config, new_config):
    result = copy.deepcopy(config)
    for key, item in new_config.items():
        if key in ('clusters', 'users', 'contexts'):
            merge_list(result, key, item)
        else:
            result[key] = item
    return result


def merge_list(config, key, items):
    if key not in config:
        config[key] = items
        return

    existing = {item['name']: item for item in config[key] if 'name' in item}
    for item in items:
        existing_item = existing.get(item['name'])
        if existing_item:
            merge_dict(existing_item, item)
        else:
            config[key].append(item)


def merge_dict(d1, d2):
    for key, value in d2.items():
        if key in d1:
            existing = d1[key]
            if isinstance(existing, dict) and isinstance(value, dict):
                merge_dict(existing, value)
            else:
                d1[key] = value
        else:
            d1[key] = value


def get_current_namespace():
    config = read_config()
    for context in config.get('contexts', []):
        if 'current-context' in config and context['name'] == config['current-context']:
            if 'namespace' in context['context']:
                return context['context']['namespace']
    return 'default'


def get_current_context():
    config = read_config()
    return config.get('current-context')
