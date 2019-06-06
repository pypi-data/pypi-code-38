

from setuptools import setup, find_packages

test_deps = ['mock', 'pytest']

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='snakebox',
      version='1.0.8',
      description='Simple click based interface for managing Virtualbox VMs',
      long_description=long_description,
      long_description_content_type="text/markdown",
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'License :: OSI Approved :: MIT License',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
      ],
      url='https://github.com/vossenv/pybox',
      maintainer='Danimae Vossen',
      maintainer_email='vossen.dm@gmail.com',
      license='MIT',
      packages=find_packages(),
      package_data={
          'snakebox': ['settings.yml', 'vmfile.txt'],
      },
      install_requires=[
          'click',
          'pyyaml'
      ],
      extras_require={
          ':sys_platform=="win32"': [
              'pywin32-ctypes',
              'pywin32'
          ],
          'test': test_deps,
      },
      tests_require=test_deps,
      entry_points={
          'console_scripts': [
              'snakebox = snakebox.app:cli',
          ]
      },
)

# twine upload --repository testpypi dist/*.tar.gz dist/*.whl
# twine upload dist/*.tar.gz dist/*.whl