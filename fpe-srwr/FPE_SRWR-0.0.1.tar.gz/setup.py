from setuptools import setup, find_packages

setup(
    name = 'FPE_SRWR',
    version = '0.0.1',
    keywords = ('Supervised learning', 'Random Walk'),
    description = 'A supervised network-based random walk method to partition samples and discover biological processes',
    license = 'MIT License',

    author = 'wuyue',
    author_email = 'wuyue@stu.xidian.edu.cn',
	project_urls={
            'Documentation': 'https://github.com/yuedongwi123/FPE_SRWR_package',
            'Funding': 'https://donate.pypi.org',
            'Source': 'https://github.com/yuedongwi123/FPE_SRWR_package',
            'Tracker': 'https://github.com/yuedongwi123/FPE_SRWR_package',
      },
    packages = find_packages(),
    include_package_data = True,
    platforms = 'any',
	python_requires='>=2.7',

    install_requires = [],
)