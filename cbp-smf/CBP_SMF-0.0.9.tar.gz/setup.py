from setuptools import setup, find_packages

setup(
    name = 'CBP_SMF',
    version = '0.0.9',
    keywords = ('Data integration', 'multi-view NMF'),
    description = 'A NMF-based method to discover biological pattern in multi-view data',
    license = 'MIT License',

    author = 'wuyue',
    author_email = 'wuyue@stu.xidian.edu.cn',
	project_urls={
            'Documentation': 'https://github.com/yuedongwi123/CBP_SMF_package',
            'Funding': 'https://donate.pypi.org',
            'Source': 'https://github.com/yuedongwi123/CBP_SMF_package',
            'Tracker': 'https://github.com/yuedongwi123/CBP_SMF_package',
      },
    packages = find_packages(),
    include_package_data = True,
    platforms = 'any',
	python_requires='>=2.7',

    install_requires = [],
)