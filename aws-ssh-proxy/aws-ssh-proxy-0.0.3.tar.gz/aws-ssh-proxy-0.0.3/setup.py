from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name='aws-ssh-proxy',
    version='0.0.3',
    description='ssh proxy command for AWS EC2 instances',
    keywords='aws ssh ec2 amazon proxycommand proxy-command',
    long_description=readme(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Topic :: System :: Systems Administration',
    ],
    url='https://gitlab.com/potyl/aws-ssh-proxy/',
    author='Emmanuel Rodriguez',
    author_email='emmanuel.rodriguez@gmail.com',
    license='MIT',
    install_requires=[
        'boto3',
    ],
    scripts=[
        'bin/aws-ssh-proxy',
    ],
    zip_safe=False,
)
