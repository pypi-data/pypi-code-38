from setuptools import setup

setup(
    name="edx_user_state_client",
    version="1.1.1",
    packages=[
        "edx_user_state_client",
    ],
    install_requires=[
        "PyContracts>=1.7.1,<2.0.0",
        "edx-opaque-keys>=1.0.0,<2.0.0",
        "xblock>=0.4,<2.0.0",
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
)
