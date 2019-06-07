from setuptools import setup

setup(
    # Needed to silence warnings
    name='printbig',
    url='https://github.com/AlexAndrei98/testpackage',
    author='Alex Andrei',
    author_email='alexandrei1998@hotmail.it',
    # Needed to actually package something
    packages=['printbig'],
    # Needed for dependencies
    install_requires=['numpy'],
    # *strongly* suggested for sharing
    version='0.6.2.2',
    license='MIT',
    description='An python package that prints bigger than anyone. It prints HUGE',
    # We will also need a readme eventually (there will be a warning)
    long_description_content_type="text",
    long_description=open('Readme.txt').read(),
    # if there are any scripts
)