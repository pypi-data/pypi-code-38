from distutils.core import setup

setup(
    name="gitlab-throttle",
    version="0.0.1",
    description="Enforce a max number of pipelines per branch",
    author="Ian Norton",
    author_email="inorton@gmail.com",
    url="https://gitlab.com/cunity/gitlab-throttle",
    packages=["GitlabThrottle"],
    install_requires=["requests", "python-gitlab"],
    platforms=["any"],
    license="License :: OSI Approved :: MIT License",
    long_description="Abort old gitlab pipelines if you have too many"
)
