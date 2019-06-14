from setuptools import setup, find_packages

setup(
    name='research',
    version='0.1.2',
    description='Utility modules used for research and/or learning',
    license='MIT',
    author='Jack Blandin',
    author_email='jackblandin@gmail.com',
    url='https://github.com/jackblandin/research',
    keywords=['dqn', 'reinforcement-learning', 'machine-learning',
                'research', 'pomdp', 'python', 'deep-learning'],
    download_url='https://github.com/jackblandin/research/archive/v_01.tar.gz',
    packages=find_packages(),
    install_requires=[
        'numpy==1.15.4',
        'pandas==0.23.2',
        'scikit-learn==0.20.3',
    ],
)
