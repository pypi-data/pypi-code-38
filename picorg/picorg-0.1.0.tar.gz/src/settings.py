import json

from pathlib import Path


SETTINGS_DIR = Path(Path.home(), ".picorg")


def get(key, default_value):
    SETTINGS_DIR.mkdir(exist_ok=True)
    settings_file = SETTINGS_DIR.joinpath("settings.json")

    settings = {}
    if settings_file.is_file():
        with open(settings_file, "r") as f:
            try:
                settings = json.load(f)
            except json.JSONDecodeError as e:
                print("Unable to parse config file.")
                print(e)
                return None
    else:
        settings_file.touch(exist_ok=True)
    if key not in settings:
        settings[key] = default_value
    with open(settings_file, "w") as f:
        f.write(json.dumps(settings, sort_keys=True, indent=4))
    return settings[key]


if __name__ == "__main__":
    get("my.key", 42)
    get("some.list", [])
    get("some.list.with.values", ["a value"])
