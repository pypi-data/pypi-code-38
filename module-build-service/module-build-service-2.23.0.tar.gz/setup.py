from os import path

from setuptools import setup, find_packages


def read_requirements(filename):
    specifiers = []
    dep_links = []
    with open(filename, "r") as f:
        for line in f:
            if line.startswith("-r") or line.strip() == "":
                continue
            if line.startswith("git+"):
                dep_links.append(line.strip())
            else:
                specifiers.append(line.strip())
    return specifiers, dep_links


setup_py_path = path.dirname(path.realpath(__file__))
install_requires, deps_links = read_requirements(path.join(setup_py_path, "requirements.txt"))
tests_require, _ = read_requirements(path.join(setup_py_path, "test-requirements.txt"))

setup(
    name="module-build-service",
    description="The Module Build Service for Modularity",
    version="2.23.0",
    classifiers=["Programming Language :: Python", "Topic :: Software Development :: Build Tools"],
    keywords="module build service fedora modularity koji mock rpm",
    author="The Factory 2.0 Team",
    author_email="module-build-service-owner@fedoraproject.org",
    url="https://pagure.io/fm-orchestrator/",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    dependency_links=deps_links,
    entry_points={
        "console_scripts": [
            "mbs-upgradedb = module_build_service.manage:upgradedb",
            "mbs-frontend = module_build_service.manage:run",
            "mbs-manager = module_build_service.manage:manager_wrapper",
        ],
        "moksha.consumer": "mbsconsumer = module_build_service.scheduler.consumer:MBSConsumer",
        "moksha.producer": "mbspoller = module_build_service.scheduler.producer:MBSProducer",
        "mbs.messaging_backends": [
            "fedmsg = module_build_service.messaging:_fedmsg_backend",
            "in_memory = module_build_service.messaging:_in_memory_backend",
            # 'custom = your_organization:_custom_backend',
        ],
        "mbs.builder_backends": [
            "koji = module_build_service.builder.KojiModuleBuilder:KojiModuleBuilder",
            "mock = module_build_service.builder.MockModuleBuilder:MockModuleBuilder",
        ],
        "mbs.resolver_backends": [
            "mbs = module_build_service.resolver.MBSResolver:MBSResolver",
            "db = module_build_service.resolver.DBResolver:DBResolver",
            "local = module_build_service.resolver.LocalResolver:LocalResolver",
        ],
    },
    scripts=["client/mbs-cli"],
    data_files=[
        (
            "/etc/module-build-service/",
            [
                "conf/cacert.pem",
                "conf/config.py",
                "conf/koji.conf",
                "conf/mock.cfg",
                "conf/yum.conf",
            ],
        ),
        (
            "/etc/fedmsg.d/",
            [
                "fedmsg.d/mbs-logging.py",
                "fedmsg.d/mbs-scheduler.py",
                "fedmsg.d/module_build_service.py",
            ],
        ),
    ],
)
