from setuptools import setup

setup(
    name='django-froala-editor',
    version='3.0.0-rc.2',
    author='Dipesh Acharya',
    author_email='dipesh@awecode.com',
    maintainer='Froala Labs',
    packages=['froala_editor'],
    url='http://github.com/froala/django-froala-editor/',
    license='BSD License',
    description='django-froala-editor package helps integrate Froala WYSIWYG HTML editor with Django.',
    long_description=open('README.rst').read(),
    include_package_data=True,
    zip_safe=False,
    keywords='froala,django,admin,wysiwyg,editor,text,html,editor,rich,web',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
