from pathlib import Path

from setuptools import setup

project_base_url = 'https://github.com/lycantropos/monty/'

setup_requires = [
    'pytest-runner>=4.2',
]
install_requires = Path('requirements.txt').read_text()
tests_require = Path('requirements-tests.txt').read_text()

entry_points = {
    'console_scripts':
        [
            'monty = monty.monty:main'
        ],
}

setup(name='montemplate',
      version='0.1.2',
      description='Python project generator.',
      long_description=Path('README.md').read_text(encoding='utf-8'),
      long_description_content_type='text/markdown',
      author='Azat Ibrakov',
      author_email='azatibrakov@gmail.com',
      url=project_base_url,
      download_url=project_base_url + 'archive/master.zip',
      python_requires='>=3.5',
      setup_requires=setup_requires,
      install_requires=install_requires,
      tests_require=tests_require,
      entry_points=entry_points)
