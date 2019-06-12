from setuptools import setup

setup(
    name='edx-ccx-keys',
    version='0.2.2',
    author='edX',
    author_email='oscm@edx.org',
    description='Opaque key support custom courses on edX',
    url='https://github.com/edx/ccx-keys',
    license='AGPL',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
    ],
    packages=[
        'ccx_keys',
    ],
    install_requires=[
        'edx-opaque-keys>=1.0.1,<2.0.0',
        'six>=1.10.0,<2.0.0'
    ],
    entry_points={
        'course_key': [
            'ccx-v1 = ccx_keys.locator:CCXLocator',
        ],
        'usage_key': [
            'ccx-block-v1 = ccx_keys.locator:CCXBlockUsageLocator',
        ]
    }
)
