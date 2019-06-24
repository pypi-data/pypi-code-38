from setuptools import setup
setup(name='ethics',
      version='0.9.9.5',
      description = ("A python toolbox for ethical reasoning."),
      author='Felix Lindner',
      author_email='info@hera-project.com',
      url='http://www.hera-project.com',
      py_modules=['ethics.moralplans', 'ethics.language', 'ethics.semantics', 'ethics.principles', 'ethics.tools', 'ethics.verbalizer', 'ethics.explanations', 'ethics.solver', 'ethics.argumentation'],
      install_requires=['python-sat']
      )
