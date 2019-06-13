from setuptools import setup

setup(
    name='txt_when_done',
    version='0.0.5',
    packages=['txt_when_done'],
    url='https://github.com/willhk/txt-when-done',
    license='MIT',
    author='willhk',
    author_email='will.haeck@gmail.com',
    description='Magic command to send a text when a jupyter cell completes.',
    install_requires=['ipython', 'jupyter', 'twilio'],
    classifiers=[
        'Programming Language :: Python :: 3.7',
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)