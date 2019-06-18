import os


class Packages:
    def __init__(self):
        self.packages = self._get_packages()

    def __str__(self):
        # Run pip list command
        return str(os.popen('pip list').read())

    def __iter__(self):
        # Pack packages dictionary into a list of tuples
        return iter([(name, version) for name, version in self.packages.items()])

    @staticmethod
    def _get_packages():
        """Retrieve a list of installed pacakges"""
        # Run pip freeze command
        pip_freeze = os.popen('pip freeze').read()

        # Create dictionary of packages
        return {package.split('==')[0]: package.split('==')[1] for package in pip_freeze.strip().split('\n')}

    def installed(self, package_name):
        """
        Check if a particular Python package is installed.

        :param package_name: Name of the package
        :return: True or False
        """
        status = True if package_name.lower() in [str(key.lower()) for key in self.packages.keys()] else False
        return status


def main():
    print(Packages())


if __name__ == '__main__':
    main()
