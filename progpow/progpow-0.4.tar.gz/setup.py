from setuptools import setup, find_packages, Distribution
from setuptools.command.install import install
from build_helper import ensure_system, ensure_local
from wheel.bdist_wheel import bdist_wheel

class InstallClass(install):
    def run(self):
        ensure_system()
        install.run(self)


class BDistClass(bdist_wheel):
    def run(self):
        ensure_local()
        bdist_wheel.run(self)

setup(
    name="progpow",
    version="0.4",

    description='FFI bindings to progpow clib',
    url='https://github.com/WTRMQDev/progpow',
    author='Crez Khansick',
    author_email='TetsuwanAtomu@tuta.io',
    license='MIT',

    setup_requires=['cffi>=1.3.0', 'pytest-runner==2.6.2', 'wheel'],
    install_requires=['cffi>=1.3.0', 'wheel'],
    tests_require=['pytest==2.8.7'],

    packages=find_packages(),
    ext_package="progpow",
    data_files = [('lib', ['libprogpow0_9_2.so','libprogpow0_9_3.so'])],
    cffi_modules=[
        "ffi.py:ffi0_9_2", "ffi.py:ffi0_9_3"
    ],
    cmdclass = {'install':InstallClass, 'bdist_wheel':BDistClass},
    distclass=Distribution,
    include_package_data = True,
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries",
        "Topic :: Security :: Cryptography"
    ],
    zip_safe=False,

)
