import os


def find_story_yml():
    """Finds './story.yml'."""
    path = _find_story_yml('story.yml')
    if not path:
        path = _find_story_yml('asyncy.yml')

    return path


def _find_story_yml(file_name):
    current_dir = os.getcwd()
    while True:
        if os.path.exists(f'{current_dir}{os.path.sep}{file_name}'):
            return f'{current_dir}{os.path.sep}{file_name}'
        elif current_dir == os.path.dirname(current_dir):
            break
        else:
            current_dir = os.path.dirname(current_dir)

    return None


def get_app_name_from_yml() -> str:
    file = find_story_yml()
    if file is None:
        return None
    import yaml

    with open(file, 'r') as s:
        return yaml.safe_load(s).pop('app_name')


def get_asyncy_yaml(must_exist=True) -> dict:
    file = find_story_yml()

    # Anybody calling this must've already checked for this file presence.
    if must_exist:
        assert file is not None

    try:
        import yaml

        with open(file, 'r') as s:
            return yaml.safe_load(s)
    except Exception:
        return {}
