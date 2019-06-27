from distutils.core import setup

setup(
    name='mongoengine-serialize',
    version='1.2.8',
    description='Mongoengine serializer',
    author='Jeffrey Marvin Forones',
    author_email='aiscenblue@gmail.com',
    license='MIT',
    url='https://github.com/aiscenblue/mongoengine_serialize',
    packages=['mongoengine_serialize'],
    keywords=['serializer', 'mongoengine', 'mongoengine_serialize'],  # arbitrary keywords
    install_requires=['mongoengine', 'bson'],
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ]
)
