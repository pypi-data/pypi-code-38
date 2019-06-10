from setuptools import setup, find_packages

setup(
    name="xintian",
    version="0.0.6",
    author="huangxinping",
    author_email="o0402@outlook.com",
    description="A micro service framework for Sanic, so easy.",
    license="MIT",
    url="https://github.com/huangxinping/xintian",  # project home page, if any
    keywords = ['micro', 'service', 'sanic', 'flask'],
    packages=find_packages(),

    install_requires=[
        'sanic>=19.3.1',
        'sanic-openapi>=0.5.3',
        'sanic-useragent>=0.1.2',
        'sanic-sentry>=0.1.7',
        'sanic-compress>=0.1.1',
        'sanic-cors>=0.9.8',
        'asyncio-redis>=0.15.1',
        'aiomysql>=0.0.20',
        'motor>=2.0.0',
        'uvloop>=0.12.0',
        'aiohttp>=3.5.4',
        'pyyaml>=5.1',
        'jaeger-client>=4.0.0',
    ],
    package_data={
        'xintian': ['*.py', '*.yml'],
    },
)
