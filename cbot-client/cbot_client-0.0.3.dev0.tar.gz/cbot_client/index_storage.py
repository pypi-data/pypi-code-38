import os
import yaml

USER_CHANNEL = "cbot/stable"


class IndexStorage(object):

    def __init__(self, base_path):
        self.base_path = base_path
        if not os.path.exists(os.path.join(self.base_path, "recipes")):
            raise Exception("Index repository not found at: {}".format(base_path))

    @property
    def recipes_folder(self):
        return os.path.join(self.base_path, "recipes")

    def real_recipe_folder(self, name, version):
        best = version
        if os.path.exists(self.config_yml_path(name)):
            data = self.load_config_yml(name)
            if "versions" in data and version in data["versions"] and \
                    "folder" in data["versions"][version]:
                 best = data["versions"][version]["folder"]
        return os.path.abspath(self.recipe_folder(name, best))

    def recipe_folder(self, name, folder):
        return os.path.join(self.package_folder(name), folder)

    def conanfile_path(self, name, folder):
        return os.path.join(self.package_folder(name), folder, "conanfile.py")

    def package_folder(self, name):
        return os.path.join(self.recipes_folder, name)

    def config_yml_path(self, name):
        return os.path.join(self.recipes_folder, name, "config.yml")

    @property
    def package_names(self):
        return [n for n in os.listdir(self.recipes_folder)
                if os.path.isdir(os.path.join(self.recipes_folder, n))]

    def folders(self, name):
        try:
            return [n for n in os.listdir(self.package_folder(name))
                    if os.path.isdir(os.path.join(self.package_folder(name), n))]
        except IOError:
            return []

    def versions(self, name):
        if os.path.exists(self.config_yml_path(name)):
            data = self.load_config_yml(name)
            if "versions" in data:
                return [list(k.keys())[0] for k in data["versions"]]
        else:
            if not os.path.exists(self.package_folder(name)):
                return []
            return [n for n in os.listdir(self.package_folder(name))
                    if os.path.isdir(os.path.join(self.recipes_folder, n))]

        return ["1.0"]

    def add_new_version(self, name, version, folder):
        element = {"folders": folder}

        recipe_folder = self.recipe_folder(name, folder)
        if not os.path.exists(recipe_folder):
            os.makedirs(recipe_folder)

        if os.path.exists(self.config_yml_path(name)):
            data = self.load_config_yml(name)
            if "versions" not in data:
                data["versions"] = {}
            data["versions"][version] = element

            with open(self.config_yml_path(name), "w") as fl:
                contents = yaml.dump(data)
                fl.write(contents)
        else:  # If folder is "all" for example, we suppose we want to support multiple
            if version != folder:
                with open(self.config_yml_path(name), "w") as fl:
                    data = {"versions": [element]}
                    contents = yaml.dump(data)
                    fl.write(contents)

        print("Added new version {}/{}".format(name, version))

    def generate_recipe_for_version(self, name, version, folder, header_only=False):
        recipe_folder = self.recipe_folder(name, folder)
        cf_path = os.path.join(recipe_folder, "conanfile.py")
        if not os.path.exists(cf_path):
            import subprocess
            # FIXME: Use a template for c3i with "-m" when it allow to pass an abs path
            cmd = "conan new {}/{}@{} -t{}".format(name, version, USER_CHANNEL,
                                                   " -i" if header_only else "")
            p = subprocess.Popen(cmd.split(" "), cwd=recipe_folder, stdout=subprocess.DEVNULL)
            code = p.wait()
            if code != 0:
                raise Exception("conan new command failed")

            # Override the conanfile
            tname = "layout.txt" if not header_only else "header_only_layout.txt"
            template = os.path.join(os.path.dirname(__file__), "assets", tname)
            with open(template) as fn:
                contents = fn.read()
                ret = contents.format(name=name, version=version)
            with open(cf_path, "w") as fn:
                fn.write(ret)

    def add_entry_to_conandata_yml(self, name, version, folder, url, the_hash, hash_type):
        # Create conandata.yml
        recipe_folder = os.path.join(self.recipes_folder, name, folder)
        entry = {"url": url, hash_type: the_hash}
        data = {"sources": {version: entry}}
        data_yml_path = os.path.join(recipe_folder, "conandata.yml")
        yml_file = os.path.exists(data_yml_path)
        if yml_file:
            with open(data_yml_path) as fl:
                contents = fl.read(yml_file)
                data = yaml.safe_load(contents)
                data["sources"][version].append(entry)

        with open(data_yml_path, "w") as fl:
            contents = yaml.dump(data)
            fl.write(contents)

    def load_config_yml(self, name):
        with open(self.config_yml_path(name)) as fl:
            contents = fl.read()
            return yaml.safe_load(contents)

    def save_config_yml(self, name, data):
        contents = yaml.safe_dump(data)
        with open(self.config_yml_path(name), "w") as fl:
            fl.write(contents)

