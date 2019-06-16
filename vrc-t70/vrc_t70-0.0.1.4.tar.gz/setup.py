from setuptools import find_packages, setup

from vrc_t70 import __version__

try:  # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError:  # for pip <= 9.0.3
    from pip.req import parse_requirements

PACKAGE_NAME = "vrc_t70"

README_FILE = "README.md"
install_reqs = parse_requirements("requirements.txt", session=False)
requirements = [str(ir.req) for ir in install_reqs]
hyphen_package_name = PACKAGE_NAME.replace("_", "-")


def read_file_content(file_name):
    with open(file_name) as f:
        return f.read()


if __name__ == "__main__":
    packages_to_remove = ["tests"]
    packages = find_packages()

    for item in packages_to_remove:
        if item in packages:
            packages.remove(item)

    setup(
        name=PACKAGE_NAME,
        packages=packages,
        version=__version__,
        description="Module to support VRC-T70 hardware",
        long_description="Please read https://github.com/JFF-Bohdan/vrc_t70/blob/master/README.md for information",
        author="Bohdan Danishevsky",
        author_email="dbn@aminis.com.ua",
        url="http://github.com/JFF-Bohdan/vrc_t70",
        keywords=["VRC-T70", "thermo sensors", "DS18B20"],
        setup_requires=["pytest-runner"],
        tests_require=["pytest"],
        install_requires=requirements,
        classifiers=[],
        license="MIT",
        zip_safe=False,
        entry_points = {
            "console_scripts": [
                "find_devices=vrc_t70.command_line.find_devices:main",
                "get_temperatures=vrc_t70.command_line.get_temperatures:main",
                "list_ports=vrc_t70.command_line.list_ports:main"
            ],
        }
    )
