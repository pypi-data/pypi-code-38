import yaml

def get_config(filename, environment="development"):
    file_path = "config/"+filename
    with open(file_path, "r") as stream:
        try:
            config = yaml.safe_load(stream)
            return config[environment]
        except yaml.YAMLError as exc:
            return exc
