import os
import setuptools

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

TEST_REQUIREMENTS = [
    'pytest',
    'pytest-cov',
    'pytest-django'
]

setuptools.setup(
    name='djangocms-cameraslider',
    version='0.1.3',
    license='MIT License',
    description='A Django CMS image slider plugin that uses Camera Slider/Slideshow.',
    long_description=README,
    long_description_content_type="text/markdown",
    url='https://github.com/knyazz/djangocms-cameraslider',
    author='Evgenii Smirnov',
    author_email='knyazz@gmail.com',
    keywords='djangocms-cameraslider, cameraslider, django, image-slider',
    packages=[
        'djangocms_cameraslider',
    ],
    include_package_data=True,
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=[
        'django-cms>=3.5.3',
        'django-mptt==0.9.0',
        'django-filer',
        'easy-thumbnails',
        'djangocms-text-ckeditor',
    ],
    setup_requires=['pytest-runner'],
    tests_require=TEST_REQUIREMENTS
)
