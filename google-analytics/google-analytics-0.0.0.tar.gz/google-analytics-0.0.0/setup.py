from setuptools import setup, find_packages

setup(
    name='google-analytics',
    version="0.0.0",
    description='A google analytics client library',
    url='https://github.com/davebelais/google-analytics',
    author='David Belais',
    author_email='david@belais.me',
    license='MIT',
    classifiers=[
        # 'Development Status :: 1 - Planning',
        'Development Status :: 2 - Pre-Alpha',
        # 'Development Status :: 3 - Alpha',
        # 'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='google analytics',
    packages=find_packages(),
    install_requires=[
        "sob"
    ],
)
